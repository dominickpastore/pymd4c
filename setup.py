from setuptools import setup, Extension

with open("README.md", "r") as f:
    long_description = f.read()

md4c = Extension('md4c',
    sources=[
        'pymd4c.c'
    ],
    #TODO Finish this
)

setup(
    name="PyMD4C",
    # Version should track MD4C version plus an extra segment for PyMD4C-only
    # updates
    version="0.4.3.0dev0",
    author="Dominick C. Pastore",
    author_email="dominickpastore@dcpx.org",
    description="Python bindings for MD4C",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dominickpastore/pymd4c",
    ext_modules=[md4c],
    #TODO finish this
)
