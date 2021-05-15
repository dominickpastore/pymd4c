![Release Status](https://github.com/dominickpastore/pymd4c/workflows/Release/badge.svg)
![Test Status](https://github.com/dominickpastore/pymd4c/workflows/Test/badge.svg?branch=dev)

PyMD4C
======

Python bindings for the very fast [MD4C] Markdown parsing and rendering
library.

- Documentation: [TODO][docs]
- GitHub: [https://github.com/dominickpastore/pymd4c][GitHub]
- PyPI: [https://pypi.org/project/pymd4c/][PyPI]
- Changelog: [https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md][changelog]
- Issues: [https://github.com/dominickpastore/pymd4c/issues][issues]

Overview
--------

The [MD4C] C library provides a SAX-like parser that uses callbacks to return
the various blocks, inlines, and text it parses from the Markdown input. In
addition, it provides an HTML renderer built on top of the parser to provide
HTML output directly.

PyMD4C provides Python bindings for both. The goal is to provide a simple and
fast interface for applications that just need to translate Markdown to HTML,
while providing flexibility for applications that need to do more.

Brief installation instructions and examples are below, but see the [full
documentation][docs] for more detail.

Installation from PyPI
----------------------

PyMD4C is available on PyPI under the name [`pymd4c`][PyPI]. Install it with
pip as you would any other Python package:

    pip install pymd4c

This is the recommended method to obtain PyMD4C. It should work well on most
Linux distributions, Windows, and macOS, but since it contains a C module, it
must be built for each platform specifically. Those running on uncommon
architectures or old versions of their OS may find that a prebuilt module isn't
available. (If a build is not available or working for your platform and you
think it should be, consider opening a [GitHub issue][issues].)

For more detailed installation instructions, including building from source
(which should work on virtually any platform), see the "Installation" page in
the [full documentation][docs].

Basic Usage
-----------

Once PyMD4C is installed, generating HTML from Markdown is as simple as the
following:

```python
import md4c

with open('README.md', 'r') as f:
    markdown = f.read()

renderer = md4c.HTMLRenderer()
html = renderer.parse(markdown)
```

This is just the most basic example to get you up and running ASAP. There are
several options for customizing MD4C's parsing and HTML generation behavior, as
well as other APIs for tasks other than generating HTML. The [full
documentation][docs] walks through all of those features.

Contributions
-------------

Thank you for your interest in contributing to PyMD4C! The "Contributing to
PyMD4C" page in the [documentation][docs] has some information that should
prove helpful.

License
-------

This project is licensed under the MIT license. See the `LICENSE.md` file for
details.

[MD4C]: https://github.com/mity/md4c
[GitHub]: https://github.com/dominickpastore/pymd4c
[PyPI]: https://pypi.org/project/pymd4c/
[changelog]: https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md
[issues]: https://github.com/dominickpastore/pymd4c/issues
[docs]: TODO
