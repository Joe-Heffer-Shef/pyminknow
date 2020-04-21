# minKNOW mock server

This code will emulate a minKNOW machine using its
[gRPC LIMS interface](https://github.com/nanoporetech/minknow_lims_interface).

# Installation

The service expects the Python modules for the gRPC interface to be in `pyminknow/minknow/rpc`.

Follow this tutorial to generate the Python code from the `.proto` files: gRPC Basics - 
Python [Generating client and server code](https://grpc.io/docs/tutorials/basic/python/#generating-client-and-server-code).
(See also: gRPC [Python Generated Code Reference](https://grpc.io/docs/reference/python/generated-code/))

To enable these files to be imported as Python modules, you need to create `__init__.py` files in each directory.

```bash
$ touch pyminknow/minknow/__init__.py pyminknow/minknow/rpc/__init__.py
```

# Usage

The service may run in a container or in a Python environment.

## Container

```bash
$ docker build . -t pyminknow:latest
$ docker run --publish 5901:5901 --name min pyminknow:latest
```

## Python

```bash
$ pip install -r requirements.txt
$ python pyminknow
```

