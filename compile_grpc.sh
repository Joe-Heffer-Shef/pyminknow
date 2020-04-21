#!/bin/sh

mkdir pyminknow/minknow/rpc --parents
touch pyminknow/minknow/__init__.py pyminknow/minknow/rpc/__init__.py
python -m grpc_tools.protoc --python_out=pyminknow --grpc_python_out=pyminknow --proto_path=minknow_lims_interface minknow_lims_interface/minknow/rpc/*.proto \
