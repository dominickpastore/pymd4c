#!/bin/bash

set -e -u -x

md4c_version=$(python3 setup.py --version | awk -F. '{print $1"."$2"."$3}')
git clone --branch release-${md4c_version} --depth 1 https://github.com/mity/md4c.git $1
