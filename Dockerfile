FROM python:3.7-slim-buster

LABEL maintainer="Joe Heffer <j.heffer@sheffield.ac.uk>" \
version=0.0.2

# Create non-root user to run the daemon
RUN useradd minknow --create-home
WORKDIR /home/minknow

EXPOSE 9501 22

# Get security updates and install packages
RUN apt-get update && apt-get --yes install openssh-server rsync \
  # Clear apt cache to reduce image size https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#run
  && rm -rf /var/lib/apt/lists/* && apt-get clean \
  && pip install --upgrade pip

# Copy all files into container except those specified in .dockerignore
COPY . .

RUN useradd minit --create-home
COPY .ssh .
# Create a SSH user for the COGUK system with passwordless access
RUN mkdir /home/minit/.ssh \
&& cat .ssh/id_rsa.pub >> /home/minit/.ssh/authorized_keys

# Create sequencer data directory
RUN mkdir /data && chown minknow:minknow /data

# Install Python packages
RUN pip install pyminknow

# Compile gRPC modules
RUN sh compile_grpc.sh

USER minknow

CMD ["python", "pyminknow"]
