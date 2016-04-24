#!/bin/sh -e
#: Shell script to build and install a Python 3 package as a Debian package.
#: This requires stdeb from the Python Package Index.

python3 -m unittest
sudo python3 setup.py --command-packages=stdeb.command install_deb
sudo rm -rf dist deb_dist MANIFEST
