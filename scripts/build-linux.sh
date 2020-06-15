#!/bin/bash
# See https://github.com/pypa/python-manylinux-demo

set -e -u -x
shopt -s nullglob

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/dist/
    fi
}



# Install MD4C
yum install -y cmake3
mkdir /io/md4c-lib/build
(
    cd /io/md4c-lib/build
    cmake3 -DCMAKE_INSTALL_LIBDIR:PATH=/usr/local/lib ..
    make
    make install
)
#ldconfig

# Compile wheels
all_pybins=/opt/python/cp[^2][6-9]-*/bin /opt/python/cp[^2][0-9][0-9]*-*/bin
ls -d $all_pybins
for pybin in $all_pybins; do
    "${pybin}/pip" wheel /io/ --no-deps -w dist/
done

# Bundle external shared libraries into the wheels
for whl in dist/*.whl; do
    repair_wheel "$whl"
done
