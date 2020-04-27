from setuptools import setup, Extension

with open("README.md", "r") as f:
    long_description = f.read()

class PkgconfigExtensionList(list):
    """A subclass of list that does not require the pkgconfig module for
    initialization, but imports it and updates the list as soon as it is
    accessed."""
    def __init__(self, exts):
        """Create PkgconfigExtensionList from the given list of extension info.
        Each extension must be a dict where keys are the arguments for
        Extension() with one additional key, 'libs', a string to be passed to
        pkgconfig.parse()."""
        super().__init__(exts)
        self.pkgconfig_ready = False

    def _fetch_pkgconfig(self):
        # If pkgconfig already fetched, return
        if self.pkgconfig_ready:
            return

        import pkgconfig

        # Use 'libs' key to add pkgconfig info to all extensions
        orig_extensions = super().copy()
        super().clear()
        for extension in orig_extensions:
            # If no 'libs' key, add as-is
            try:
                libs = extension['libs']
            except KeyError:
                super().append(Extension(**extension))

            # Add pkgconfig info
            del extension['libs']
            for k, v in pkgconfig.parse(libs).items():
                try:
                    extension[k].extend(v)
                except KeyError:
                    extension[k] = v
            super().append(Extension(**extension))

        # Mark pkgconfig fetch complete
        self.pkgconfig_ready = True

    def __iter__(self):
        self._fetch_pkgconfig()
        return super().__iter__()

    def __getitem__(self, key):
        self._fetch_pkgconfig()
        return super().__getitem__(key)

extensions = PkgconfigExtensionList([
    {
        'name': 'md4c._md4c',
        'sources': [
            'src/pymd4c.c',
        ],
        'libs': 'md4c md4c-html',
    },
    {
        'name': 'md4c._enum_consts',
        'sources': [
            'src/enum_consts.c',
        ],
        'libs': 'md4c',
    },
])

setup(
    name="PyMD4C",
    version="0.4.3.0dev2",
    author="Dominick C. Pastore",
    author_email="dominickpastore@dcpx.org",
    description="Python bindings for MD4C",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dominickpastore/pymd4c",
    setup_requires=[
        'pkgconfig',
    ],
    packages=[
        'md4c',
    ],
    ext_modules=extensions,
    classifiers=[
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires='>=3.6',
    zip_safe=False,
)
