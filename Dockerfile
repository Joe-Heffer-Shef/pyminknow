FROM python:3.7-slim-buster

LABEL maintainer="Joe Heffer <j.heffer@sheffield.ac.uk>" \
version=0.0.1

# Create non-root user to run the daemon
RUN useradd minknow --create-home
WORKDIR /home/minknow

EXPOSE 9501 22

# Get security updates
RUN apt-get update && apt-get --yes install openssh-server
RUN pip install --upgrade pip

# Create a SSH user for the COGUK system with passwordless access
RUN useradd minit --create-home \
&& mkdir /home/minit/.ssh
COPY .ssh/id_rsa.pub /home/minit/.ssh/authorized_keys

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all files into container except those specified in .dockerignore
COPY . .

# Compile gRPC modules
RUN sh compile_grpc.sh

USER minknow

CMD ["python", "pyminknow"]
