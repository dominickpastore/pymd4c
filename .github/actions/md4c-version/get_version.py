from __future__ import print_function
import json
import os

with open('about.json') as f:
    about = json.load(f)

min_version = about['md4c-version']['min']
max_version = about['md4c-version']['max']

with open(os.environ['GITHUB_OUTPUT'], 'w') as f:
    print('md4c=' + max_version, file=f)
    print('md4c-min=' + min_version, file=f)
