Some Notes on Testing
=====================

Test procedure:

```
pip install .[test]
flake8 setup.py md4c/
pytest -vv test/
```

Optionally, `--md4c-version X.Y.Z` can be added to the `pytest` line and it
will skip any tests that require a later version of MD4C.

Specification files
-------------------

Specifications and sample test cases reside in the `specs/` directory.

### `spec.txt`

From vanilla CommonMark.

Note that the normalization filter converts self-closing tags (e.g. `<img />`)
to non-self-closing tags. For the most part, this is correct, since MD4C does
not self-close anything (as allowed by HTML5), but it causes problems for a
handful of raw HTML test cases. The self-closing tags need to be manually
removed from these. They should be easy to identify when running ``pytest``
after downloading a new `spec.txt`.

### `gfm.txt`

Spec and test cases for GitHub Flavored Markdown. This contains just GitHub's
extensions. Unfortunately, there's no easy way to get them separate from the
main spec. (There is a file in their `cmark-gfm` repository,
`test/extensions.txt`, but it's very out of date.) The only way to get this
seems to be to open the full spec and pull out the sections for GitHub
extensions. A nontrivial amount of work, unfortunately.

There are some differences between MD4C's table parsing and GFM's. See:
* <https://github.com/mity/md4c/issues/136> (`|` in code blocks does not become
  a table cell delimiter, `\|` in code blocks within a table are treated
  literally)
* <https://github.com/mity/md4c/issues/137> (Tables with differing number of
  elements in the header row and the delimiter row are still treated as tables)

Why not just use GitHub's `spec.txt` as an overall starting point? Because it's
missing some test cases from CommonMark's `spec.txt`, for some reason.

### Others

The rest are specification files [directly from
MD4C](https://github.com/mity/md4c/tree/master/test). Files that require parser
options are modified to include annotations for them.

Any tests that require at least a certain version of MD4C have the annotation
`md4c-X.Y.Z`. These tests will be skipped when `--md4c-version` is provided
with an earlier version.
