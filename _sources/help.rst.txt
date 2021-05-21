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
