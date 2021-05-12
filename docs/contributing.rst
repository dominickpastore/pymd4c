Contributing to PyMD4C
======================

Thank you for your interest in contributing to PyMD4C!

Reporting Issues
----------------

If you have found an issue with PyMD4C but do not have the time or do not feel
comfortable making a fix yourself, feel free to `submit an issue`_ on GitHub.

All issues and bug reports are welcome, but there are a few things you can do
to help things move more smoothly:

- Mention what versions of Python and PyMD4C you have installed. If you are not
  sure, you can check with::

      python3 --version
      pip show pymd4c

- Describe the incorrect output/behavior you are observing and the
  output/behavior you expected.

- If possible, provide sample Python code that reproduces the issue, or at the
  very least, mention which class and any options you were using.

- If the issue happens with specific input, provide an example Markdown
  document (preferably less than 10 lines or so) that reproduces the issue.

- Any other information you think might be relevant (e.g. error messages, stack
  traces, your OS and CPU architecture, etc., depending on the type of issue).

Of course, some of the above only applies to certain types of issues. For
example, if you ran into an issue building PyMD4C from source, providing sample
Python code and input do not make sense (but you *would* want to provide some
of the extra information mentioned in the last bullet point).

But just to reiterate, *all* issues and bug reports are welcome, even if they
are light on details.

Feature Requests
----------------

If there is a feature missing from PyMD4C that you would like to see added,
feel free to `submit an issue`_ on GitHub for this as well.

If you feel ambitious, you can even implement the feature youself and `submit a
pull request`_. If you do so, make sure you read the section below.

Code Contributions
------------------

First off, thank you for your interest in improving PyMD4C! If you have code
you would like to contribute, please feel free to `submit a pull request`_ on
GitHub.

All code contributions are appreciated, but there are a few guidelines that
make it more likely that a PR can be accepted:

- Generally speaking, the ``master`` branch is reserved for released code only.
  Development happens on the ``dev`` branch. That is the branch you should
  start working from, and the branch you should submit pull requests to. (If
  you submit a pull request to ``master``, we will change it to ``dev``.)

- The automated test suite should run when pull requests are submitted. If
  there are any problems, you should do your best to fix them (or explain why
  the test is flagging when it shouldn't). Code that passes has a much higher
  chance of being accepted than code that fails. You can run the test suite
  locally with TODO is correct?::

      pip install -U .[test]
      flake8 setup.py md4c/
      pytest

- Pay attention to code style. Flake8 runs as part of the test suite. ``#noqa``
  is allowed, but with good reason.

- If you add new functionality, it has a higher chance of being merged if you
  add additional documentation and tests for the new feature (but if you don't,
  that doesn't mean it will be automatically rejected).

- Pull requests need not be related to an existing issue, but if you submit one
  that is, you should reference the issue number somewhere in the pull request.

None of these are automatic deal breakers if you do not follow them, but
following them does increase the chances of your pull request being accepted.

All code contributions will be mentioned in the CHANGELOG with attribution to
the contributor.

.. _submit an issue: https://github.com/dominickpastore/pymd4c/issues
.. _submit a pull request: https://github.com/dominickpastore/pymd4c/pull
