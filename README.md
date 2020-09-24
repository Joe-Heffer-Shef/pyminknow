# minKNOW mock server

This code will emulate a [Oxford Nanopore Technologies](https://nanoporetech.com/) gene sequencing device (e.g. [minION](https://nanoporetech.com/products/minion) or minKNOW) using its gRPC Remote Procedure Calls [LIMS interface](https://github.com/nanoporetech/minknow_lims_interface) to interact with its embedded software. This package is designed to form part of a software development environment to facilitate rapid prototyping and automated testing.

## Glossary

* **minKNOW** device manager (host software)
* **gridION** a physical device containing an array of sequencing devices
* **minION** a physical sequencing device

## See also

* Developed at The University of Sheffield, IT Services, [Research & Innovation](https://www.sheffield.ac.uk/it-services/research).
* [pyminknow](https://pypi.org/project/pyminknow/) at PyPi
* [pyminknow](https://hub.docker.com/r/jheffer/pyminknow) at Docker Hub
* [pyminknow](https://github.com/Joe-Heffer-Shef/pyminknow) at GitHub

# Installation

```bash
$ pip install pyminknow
```

# Usage

The service may run in a container or in a Python environment. To see the usage reference, run:

```bash
$ python pyminknow --help
```



## Test client

You may use `client.py` to test the functionality of the server. To get help, run:

```bash
$ python client.py --help
```

Unit tests may be used to systematically test the server functionality.

```bash
$ python -m unittest
```



## Container

The container is based on Debian Linux and uses Python 3.7 as defined in the `Dockerfile`. You may build and run the container using the commands below.

```bash
$ docker build --tag pyminknow:latest .
$ docker run --name minit --publish 5901:5901 -publish 22:22 -d pyminknow:latest
# Start the SSH service
$ docker exec -it --user root minit service ssh start
```

## Python

You should do this inside a Python 3.7 virtual environment. Install packages and then run the service. 

```bash
$ pip install pyminkow
$ python -m pyminknow
```

