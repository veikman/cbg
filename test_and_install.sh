#!/bin/bash -eu
#: Shell script to build and install package.
#: To be run where setup.py is.

PYTHON=python3
PROJECT=cbg

$PYTHON -m unittest discover
sudo $PYTHON setup.py install
sudo rm -rf dist build
