import json
with open('about.json') as f:
    about = json.load(f)
min_version = about['md4c-version']['min']
max_version = about['md4c-version']['max']
print('::set-output name=md4c::' + max_version)
print('::set-output name=md4c-min::' + min_version)
