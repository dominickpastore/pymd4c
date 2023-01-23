Help Resources
==============

Frequently Asked Questions
--------------------------

Why another Markdown library?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The primary reason is performance. Most applications that work with Markdown
are going to be interested in one thing and one thing only: generating HTML.
For that, there are two performance advantages from offloading the task to C:

- C is more efficient with CPU cycles and memory usage than Python
- A bulk processing task like this can release CPython's `Global Interpreter
  Lock`_ while it is not running Python code (an advantage for multithreading)

There are several C libraries for Markdown parsing, but I chose MD4C for a
couple reasons:

- It is one of the fastest Markdown parsing libraries out there (if not *the*
  fastest).
- The tests for MD4C are thorough. The author has put a lot of care into
  avoiding non-linear parsing time (meaning good protection from DOS attacks)
  and uses modern techniques like coverage testing and fuzzing. This is quite
  important considering it will likely handle untrusted input.

And since Python bindings for MD4C did not yet exist, I decided to create them.

.. _Global Interpreter Lock: https://docs.python.org/3/glossary.html#term-global-interpreter-lock

.. _why-source:

Why is pip trying to build from source?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This means pip cannot find a suitable pre-built package. Older versions of the
library had a limited number of platforms for which pre-built packages were
published, but since version 1.3.0, most common platforms should be supported.
However, if you fall into one of the following groups, pip may still need to
build from source:

- You are on an OS other than Windows, macOS, or Linux

- You are running a very old version of your OS

- On Linux with Python 3.6, you have a version of pip older than 19.3

- You are running an esoteric Linux distribution or on an esoteric architecture

Not having a pre-built package available for your platform isn't necessarily a
showstopper. Pip will happily perform a build from source if necessary. If you
are getting errors during the install, make sure you have all the prerequisites
(see :ref:`prerequisites`), then try again.

Why do I see ``error: pkg-config probably not installed: ...`` when trying to install?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pip is trying to build from source. See :ref:`why-source`

If building from source is unavoidable, make sure you install all the
prerequisites (see :ref:`prerequisites`), then try again.

Why do I see ``pkgconfig.pkgconfig.PackageNotFoundError: md4c not found`` when trying to install?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pip is trying to build from source. See :ref:`why-source`

If building from source is unavoidable, make sure you install all the
prerequisites (see :ref:`prerequisites`), then try again.

Generating These Docs Locally
-----------------------------

This documentation is generated with Sphinx_. With it installed and a local
copy of the PyMD4C repository, you can generate your own local copy of the docs
as follows::

    cd docs/
    make html

Now, you can browse the docs by opening "_build/html/index.html" in the browser
of your choice.

.. _Sphinx: https://www.sphinx-doc.org/en/master/

Human Help
----------

If you find you need a bit of human help, feel free to post in the discussions_
tab on GitHub. I do my best to keep an eye on these and respond.

Currently, there is no mailing list, IRC channel, Discord chat, or Stack
Overflow tag. The project is not yet big enough to warrant them.

.. _discussions: https://github.com/dominickpastore/pymd4c/discussions
