# minKNOW mock server

This code will emulate a minKNOW machine using its [gRPC LIMS interface](https://github.com/nanoporetech/minknow_lims_interface).

# Installation

The service expects the Python modules for the gRPC interface to be in `pyminknow/minknow/rpc`.

Follow this tutorial to generate the Python code from the `.proto` files: gRPC Basics - Python [Generating client and server code](https://grpc.io/docs/tutorials/basic/python/#generating-client-and-server-code). (See also: gRPC [Python Generated Code Reference](https://grpc.io/docs/reference/python/generated-code/))

# Usage

The service may run in a container or in a Python environment.

## Container

You may build and run the container using the commands below:

```bash
$ docker build -t pyminknow:latest .
$ docker run --name minit --publish 5901:5901 -d pyminknow:latest
# Start the SSH service
$ docker exec -it --user root minit service ssh start
```

## Python

You should do this inside a Python virtual environment. Compile the gRPC modules, install packages and then run the service.

```bash
$ sh compile_grpc.sh
$ pip install -r requirements.txt
$ python pyminknow
```

