#!/bin/bash

set -e -u -x

python_versions="3.6 3.7 3.8"
full_versions=""

# Install MD4C
mkdir md4c-lib/build
(
    cd md4c-lib/build
    cmake ..
    make
    make install
)

# Install python versions
eval "$(pyenv init -)"
for ver in $python_versions
do
    full_ver=$(
        pyenv install --list |
        grep "^ *${ver}\\.[0-9]* *\$" |
        sort -t. -k3 |
        tail -n1
    )

    pyenv install -v $full_ver
    full_versions="${full_versions} ${full_ver}"
done
pyenv global $full_versions

# Build wheels
for ver in $python_versions
do
    (
        python${ver} -m venv venv${ver}
        source venv${ver}/bin/activate
        python -m pip install --upgrade pip setuptools wheel
        python -m pip wheel . --no-deps -w dist/
        deactivate ""
    )
done
