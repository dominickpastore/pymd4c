#!/bin/bash

set -e -u -x

md4c_version=$(python << EOF
import json

with open('about.json') as f:
    about = json.load(f)

version_components = about['version'].split('.')
print('.'.join(version_components[0:3]))
EOF
)

git clone --branch release-${md4c_version} --depth 1 https://github.com/mity/md4c.git $1
