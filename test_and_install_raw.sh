#!/bin/sh
#: Shell script to build and install a Python3 package using basic distutils.

python3 -m unittest discover || exit 1
sudo python3 setup.py install
sudo rm -rf dist build
