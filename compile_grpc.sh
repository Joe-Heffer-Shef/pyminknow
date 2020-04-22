#!/bin/sh

# Stop on errors
set -e

# Create directory structure
mkdir pyminknow/minknow/rpc --parents

# Enable module imports
touch pyminknow/minknow/__init__.py pyminknow/minknow/rpc/__init__.py

# Run compiler
python -m grpc_tools.protoc --python_out=pyminknow --grpc_python_out=pyminknow --proto_path=minknow_lims_interface minknow_lims_interface/minknow/rpc/*.proto \
