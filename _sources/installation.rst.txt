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

2. A prebuilt package is not available for your platform, and pip could not
   build it from source (likely because the necessary dependencies were not
   available).

Regarding reason #2: Since this package contains C extensions, it is built as a
platform wheel. Prebuilt packages are available for Python 3.6+ on the
following platforms:

- Windows, 64-bit (amd64/x86-64) Python only.
- Recent versions of macOS on Intel silicon [#m1]_
- Most Linux distributions, 64-bit Python only (specifically, any distribution
  supported by manylinux2014_, amd64 architecture)

Pip will automatically attempt to build from source on other platforms, but it
will fail if the build dependencies are not available. See :ref:`prerequisites`
for information on installing them.

If a prebuilt package is not available or not working for your platform and you
think it should be, consider opening a `GitHub issue`_.

.. _Installing Packages - Python Packaging User Guide: https://packaging.python.org/tutorials/installing-packages/
.. _manylinux2014: https://github.com/pypa/manylinux
.. _GitHub issue: https://github.com/dominickpastore/pymd4c/issues

Build and Install from Source
-----------------------------

.. _prerequisites:

Prerequisites
~~~~~~~~~~~~~

This package depends on the MD4C library. It may be available through your
package manager. Otherwise, it can be built from source as follows:

1. Make sure you have CMake_ and a C compiler installed.
2. Download and extract MD4C from the `MD4C releases`_ page. See the CHANGELOG_
   or `about.json`_ for recommended versions to use. PyMD4C is tested against
   the minimum and maximum MD4C versions listed in those files. If there is a
   newer version of MD4C available, it is likely to work as well, but has not
   been tested yet.
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

.. _CMake: https://cmake.org/
.. _MD4C releases: https://github.com/mity/md4c/releases
.. _CHANGELOG: https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md
.. _about.json: https://github.com/dominickpastore/pymd4c/blob/master/about.json

.. rubric:: Footnotes

.. [#m1] Sorry M1 users, waiting for GitHub Actions to support Apple Silicon
   for GitHub-hosted runners.
