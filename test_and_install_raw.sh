#!/bin/sh -e
#: Shell script to build and install a Python 3 package using basic distutils.

python3 -m unittest
sudo python3 setup.py install
sudo rm -rf dist build
