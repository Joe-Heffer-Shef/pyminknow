FROM python:3.7-slim-buster

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

# Build gRPC server modules using ProtoBuf compiler
RUN mkdir pyminknow/minknow/rpc --parents \
&& touch /home/minknow/pyminknow/minknow/__init__.py /home/minknow/pyminknow/minknow/rpc/__init__.py \
&& python -m grpc_tools.protoc --python_out=/home/minknow/pyminknow --grpc_python_out=/home/minknow/pyminknow --proto_path=/home/minknow/minknow_lims_interface /home/minknow/minknow_lims_interface/minknow/rpc/*.proto \
&& ls -la pyminknow/minknow/rpc

USER minknow

LABEL maintainer="Joe Heffer <j.heffer@sheffield.ac.uk>" \
version=0.0.1

CMD ["python", "pyminknow"]
