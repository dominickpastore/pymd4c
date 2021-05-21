PyMD4C Documentation
====================

Welcome to the full documentation for PyMD4C, Python bindings (plus extras) for
the very fast MD4C_ Markdown parsing and rendering library.

.. _MD4C: https://github.com/mity/md4c

Using it is as simple as::

    import md4c

    with open('README.md', 'r') as f:
        markdown = f.read()

    renderer = md4c.HTMLRenderer()
    html = renderer.parse(markdown)

In more detail, the underlying MD4C C library provides two things:

- A SAX-like Markdown parser, meaning it uses callbacks to return the various
  blocks, inlines, and text it parses, as it parses
- An HTML renderer, built on top of that parser, to provide HTML output
  directly

PyMD4C provides Python bindings for both, plus some convenience features built
on top. The goal is to provide a simple and fast interface for applications
that just need to translate Markdown to HTML, while providing flexibility for
applications that need to do more.

Quick links
-----------

- `This documentation <TODO>`_ TODO
- `GitHub, README <https://github.com/dominickpastore/pymd4c>`_
- `PyPI <https://pypi.org/project/pymd4c/>`_
- `Changelog
  <https://github.com/dominickpastore/pymd4c/blob/master/CHANGELOG.md>`_
- `MD4C project <https://github.com/mity/md4c>`_

Table of Contents
-----------------

User Manual
~~~~~~~~~~~

.. This workaround with :hidden: and inserting :doc: references manually is to
   emulate :titlesonly: on the front page while still keeping the section
   headings for the sidebar. This keeps the documentation from appearing
   overly complex and overwhelming as if it had many pages when really it's
   just a handful.

   We don't do the workaround for API because the pages there are much longer,
   and a certain level of detail there is expected.

.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   generating_html
   pure_parsing
   dom_parsing

- :doc:`installation`
- :doc:`generating_html`
- :doc:`pure_parsing`
- :doc:`dom_parsing`

API
~~~

.. toctree::
   :maxdepth: 2

   api
   dom_api

Additional Information
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2
   :hidden:

   help
   contributing

- :doc:`help`
- :doc:`contributing`

Index
-----

* :ref:`genindex`
* :ref:`search`

License
-------

PyMD4C is licensed under the MIT license. See the LICENSE.md_ file in the
repository for details.

.. _LICENSE.md: https://github.com/dominickpastore/pymd4c/blob/master/LICENSE.md
