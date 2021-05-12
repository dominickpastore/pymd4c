Installation
============

Install from PyPI
-----------------

PyMD4C is available on PyPI under the name |pymd4c|_. Install it with
pip like this::

    pip install pymd4c

.. |pymd4c| replace:: ``pymd4c``
.. _pymd4c: https://pypi.org/project/pymd4c/

This is the recommended method to obtain PyMD4C. It should work well on most
Linux distributions, Windows, and macOS.

If this does not work, there are a couple potential reasons:

1. You do not have pip installed, or your version is too old. See `Installing
   Packages - Python Packaging User Guide`_.

2. Your version of Python is too old. This is a platform wheel, so it is built
   for each Python version separately. Python versions older than 3.6 are not
   supported. If your Python version is older than that, try upgrading.

3. Your platform is incompatible. Again, since it is a platform wheel, it is
   built for each supported platform separately.
   - If you are running Windows, you may be running 32-bit (x86) Python.
     Currently, only packages for 64-bit (x86-64) Python are built. If you can,
     try running 64-bit Python.
   - If you are on macOS, your macOS version might be too old.
   - If you are on Linux, you may be running on an architecture other than
     x86-64, a distribution that is too old, or a more esoteric distribution
     unsupported by manylinux2014_. (Note that many architectures
     supported by manylinux2014 are not built at this time, including x86,
     arm64, ppc64le, and s390x.)
   - If you are on some other platform, unfortunately, it is not supported by
     the pre-built packages.

If a build is not available for your platform (or you simply want to), you can
build and install from source. The instructions below should assist.

If a build is not available or not working for your platform and you think it
should be, consider opening a `GitHub issue`_.

.. _Installing Packages - Python Packaging User Guide: https://packaging.python.org/tutorials/installing-packages/
.. _manylinux2014: https://github.com/pypa/manylinux
.. _GitHub issue: https://github.com/dominickpastore/pymd4c/issues

Build and Install from Source
-----------------------------

Prerequisites
~~~~~~~~~~~~~

This package depends on the MD4C library. It may be available through your
package manager. Otherwise, it can be built from source as follows:

1. Make sure you have CMake_ and a C compiler installed.
2. Download and extract the matching release from the `MD4C releases`_
   page (e.g. for PyMD4C version W.X.Y.Z, download MD4C version W.X.Y).
3. On Unix-like systems (including macOS):

   - Inside the extracted file, run the following::

         mkdir build
         cd build
         cmake ..
         make
         # Do as root:
         make install

     The install step must be run as root. The library will install to
     /usr/local by default.
   - You may need to rebuild the ldconfig cache (also as root)::

         ldconfig

4. On Windows:

   - Inside the extracted file, run the following::

         mkdir build
         cd build
         cmake -DCMAKE_BUILD_TYPE=Release ..
         cmake --build . --config Release
         cmake --install .

     The library will install to "C:/Program Files (x86)/MD4C/" by default.

In addition, on Unix-like systems (including macOS), the ``pkg-config`` tool
must be available to build PyMD4C. After PyMD4C is built, it is no longer
required (that is, it is not a prerequisite for actually *using* PyMD4C). This
tool is likely available on your system already, so this should not be an issue
in most cases.

Finally, note that since this package uses C extensions, development headers
for Python must be installed for the build to succeed. If you are using Linux,
some distributions split these off from the main Python package. Install
``python-dev`` or ``python-devel`` to get them.

Build/Install
~~~~~~~~~~~~~

Build and install as you would for any Python source repository. Download and
extract a release or clone the repository, and run the following inside::

    pip install .

Alternatively, you can have pip fetch and build from the latest source
distribution on PyPI::

    pip install --no-binary pymd4c pymd4c

Note that on Windows, setup.py assumes the MD4C library was installed at
"C:/Program Files (x86)/MD4C/" (this is the default location when building MD4C
from source, as described above). If this is not the case, installation will
fail.

.. _MD4C releases: https://github.com/mity/md4c/releases
.. _CMake: https://cmake.org/
