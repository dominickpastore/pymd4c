from setuptools import setup, Extension

with open("README.md", "r") as f:
    long_description = f.read()

def get_extensions():
    import pkgconfig

    return [
        Extension('md4c',
            sources=[
                'src/pymd4c.c',
            ],
            **pkgconfig.parse('md4c')
        ),
    ]

setup(
    name="PyMD4C",
    version="0.4.3.0dev0",
    author="Dominick C. Pastore",
    author_email="dominickpastore@dcpx.org",
    description="Python bindings for MD4C",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dominickpastore/pymd4c",
    setup_requires=[
        'pkgconfig',
    ]
    ext_modules=get_extensions(),
    classifiers=[
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires='>=3.6',
    zip_safe=False,
)
