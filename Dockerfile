FROM python:3.7-slim-buster

LABEL maintainer="Joe Heffer <j.heffer@sheffield.ac.uk>" \
version=0.0.1

# Create non-root user
RUN useradd minknow --create-home --user-group

EXPOSE 9501

# Get security updates
#RUN apt-get update
#RUN pip install --upgrade pip

WORKDIR /home/minknow

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt --quiet

COPY pyminknow pyminknow
COPY minknow_lims_interface minknow_lims_interface
COPY compile_grpc.sh .

# Compile gRPC modules
RUN sh compile_grpc.sh

USER minknow

CMD ["python", "pyminknow"]
