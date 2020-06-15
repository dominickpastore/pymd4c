#!/bin/bash

set -e -u -x

# Install MD4C
mkdir md4c-lib/build
(
    cd md4c-lib/build
    cmake3 ..
    make
    make install
)

# Install python versions
#TODO

(
    python3.6 -m venv venv36
    source venv36/bin/activate
    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip wheel . --no-deps -w wheelhouse/
    deactivate
)

(
    python3.7 -m venv venv37
    source venv37/bin/activate
    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip wheel . --no-deps -w wheelhouse/
    deactivate
)

(
    python3.8 -m venv venv38
    source venv38/bin/activate
    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip wheel . --no-deps -w wheelhouse/
    deactivate
)
