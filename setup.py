from setuptools import setup, Extension

with open("README.md", "r") as f:
    long_description = f.read()

class PkgconfigExtensions:
    def __init__(self, exts):
        """Create PkgconfigExtensions from the given list of extension info.
        Each extension must be a dict where keys are the arguments for
        Extension() with one additional key, 'libs', a string to be passed to
        pkgconfig.parse()."""
        self.pkgconfig_ready = False
        self.extensions = exts

    def _fetch_pkgconfig(self):
        # If pkgconfig already fetched, return
        if self.pkgconfig_ready:
            return

        import pkgconfig

        # Use 'libs' key to add pkgconfig info to all extensions
        new_exts = []
        for extension in self.extensions:
            # If no 'libs' key, add as-is
            try:
                libs = extension['libs']
            except KeyError:
                new_exts.append(Extension(**extension))

            # Add pkgconfig info
            del extension['libs']
            for k, v in pkgconfig.parse(libs).items():
                try:
                    extension[k].extend(v)
                except KeyError:
                    extension[k] = v
            new_exts.append(Extension(**extension))

        # Store transformed extension list
        self.extensions = new_exts
        self.pkgconfig_ready = True

    def __iter__(self):
        self._fetch_pkgconfig()
        return iter(self.extensions)

    def __len__(self):
        return len(self.extensions)

    def __getitem__(self, key):
        self._fetch_pkgconfig()
        return self.extensions[key]

extensions = PkgconfigExtensions([
    {
        'name': 'md4c',
        'sources': [
            'src/pymd4c.c',
        ],
        'libs': 'md4c',
    },
])

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
