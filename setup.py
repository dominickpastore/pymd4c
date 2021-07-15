import sys
from setuptools import setup, Extension
import json

with open("about.json", "r") as f:
    about = json.load(f)
    del about['md4c-version']

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

    def _fetch_pkgconfig(self, extension):
        """Convert the pkgconfig keys in the dict to the proper arguments for
        Extension and then create the actual Extension"""
        # If no 'pkgconfig' key, add as-is
        try:
            libs = extension['pkgconfig']
        except KeyError:
            return Extension(**extension)

        import pkgconfig

        # Add pkgconfig info
        del extension['pkgconfig']
        for k, v in pkgconfig.parse(libs).items():
            try:
                extension[k].extend(v)
            except KeyError:
                extension[k] = v
        return Extension(**extension)

    def _fetch_pkgconfig_all(self):
        """Fetch all the pkgconfig info for all the extensions"""
        # If pkgconfig already fetched, return
        if self.pkgconfig_ready:
            return

        # Use 'libs' key to add pkgconfig info to all extensions
        orig_extensions = super().copy()
        super().clear()
        for extension in orig_extensions:
            super().append(self._fetch_pkgconfig(extension))

        # Mark pkgconfig fetch complete
        self.pkgconfig_ready = True

    def __iter__(self):
        self._fetch_pkgconfig_all()
        return super().__iter__()

    def __getitem__(self, key):
        self._fetch_pkgconfig_all()
        return super().__getitem__(key)


if sys.platform.startswith('win'):
    extensions = [
        Extension(
            'md4c._md4c',
            sources=[
                'src/pymd4c.c',
                'src/generic_parser.c',
                'src/html_renderer.c',
            ],
            include_dirs=['C:/Program Files (x86)/MD4C/include'],
            libraries=['md4c', 'md4c-html'],
            library_dirs=['C:/Program Files (x86)/MD4C/lib']),
        Extension(
            'md4c._enum_consts',
            sources=['src/enum_consts.c'],
            include_dirs=['C:/Program Files (x86)/MD4C/include'],
            libraries=['md4c'],
            library_dirs=['C:/Program Files (x86)/MD4C/lib']),
    ]
else:
    extensions = PkgconfigExtensionList([
        {
            'name': 'md4c._md4c',
            'sources': [
                'src/pymd4c.c',
                'src/generic_parser.c',
                'src/html_renderer.c',
            ],
            'pkgconfig': 'md4c md4c-html',
            'include_dirs': ['src'],
        },
        {
            'name': 'md4c._enum_consts',
            'sources': [
                'src/enum_consts.c',
            ],
            'pkgconfig': 'md4c',
            'include_dirs': ['src'],
        },
    ])

setup(
    # Most package metadata is in about.json (added below via **about)
    long_description=long_description,
    long_description_content_type="text/markdown",
    setup_requires=[
        'pkgconfig',
    ],
    packages=[
        'md4c',
        'md4c.domparser',
    ],
    ext_modules=extensions,
    python_requires='>=3.6',
    zip_safe=False,
    include_package_data=True,
    extras_require={
        'test': [
            'pytest',
            'flake8',
        ],
    },
    **about
)
