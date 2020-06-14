#!/bin/bash
# See https://github.com/pypa/python-manylinux-demo

set -e -u -x

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
}


# Install MD4C
(
    cp -r /io/md4c /tmp/md4c
    mkdir /tmp/md4c/build
    cd /tmp/md4c/build
    cmake ..
    make
    make install
    #ldconfig
)

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" wheel /io/ --no-deps -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    repair_wheel "$whl"
done
