# minKNOW mock server

This code will emulate a minKNOW machine using its [gRPC LIMS interface](https://github.com/nanoporetech/minknow_lims_interface).

Follow this tutorial to generate the Python code from the `.proto` files: gRPC Basics - Python [Generating client and server code](https://grpc.io/docs/tutorials/basic/python/#generating-client-and-server-code).

# Usage

## Container

```bash
$ docker build . -t pyminknow:latest
$ docker run --public 5901:5901 --name min .
```

## Python

```bash
$ pip install -r requirements.txt
$ python pyminknow
```

