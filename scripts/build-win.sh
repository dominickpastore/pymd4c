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

python3 -m pip wheel . --no-deps -w dist/
