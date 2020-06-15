#!/bin/bash

set -e -u -x

# Install MD4C
mkdir md4c-lib/build
(
    cd md4c-lib/build
    cmake ..
    make
    sudo make install
)
#ldconfig

# Install PyMD4C in prep for tests
pip install .

# Normally, this is handled by Travis CI, but we do it here instead since this
# is the only job that requires it.
python setup.py sdist
