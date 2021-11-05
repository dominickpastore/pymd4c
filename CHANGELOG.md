PyMD4C Changelog
================

PyMD4C uses [Semantic Versioning][semver] as of version 1.0.0. In summary, new
major versions contain breaking changes, new minor versions contain new
features, and new patch versions contain bugfixes. (There is one minor
deviation: Pre-release versions will use [PEP 440][pep440] formatting, e.g.
"1.0.0b1", not the hyphenated "1.0.0-beta.1" form specified by Semantic
Versioning.)

[Unreleased]
------------

[1.1.1] - 2021-11-05
--------------------

This PyMD4C version requires MD4C **0.4.7** or later. It has been tested
against that and the current latest version, **0.4.8**.

### Fixed

- GitHub Actions workflow does not contain fatal errors

[1.1.0] - 2021-11-04
--------------------

**Note:** This version was never fully released. The updated build workflow
contained fatal errors.

This PyMD4C version requires MD4C **0.4.7** or later. It has been tested
against that and the current latest version, **0.4.8**.

### Added

- Binary packages for Python 3.10

[1.0.0] - 2021-07-15
--------------------

With this release, the version numbering system is changing. In prior releases,
the version number tracked the MD4C version number: version W.X.Y.Z was tested
against MD4C version W.X.Y and it was the Zth release against that version.

From this release forward, releases will use [Semantic Versioning][semver].
Most MD4C releases are bugfixes, so PyMD4C generally shouldn't be that picky
about which version it's linked against. That said, the minumum supported
version and maximum tested version will be listed with each entry in the
changelog. (Newer versions are likely to work as well.)

This PyMD4C version requires MD4C **0.4.7** or later. It has been tested
against that and the current latest version, **0.4.8**.

### Fixed

- Installing projects that depend on PyMD4C will no longer fail due to missing
  headers when PyMD4C must be built from source (PR #28, thanks @EuAndreh)
- Updated installation instructions to be more accurate regarding installs
  without a prebuilt package
- Proper support for `bytes` input. Rendered output for `bytes` input will also
  be `bytes`. This allows documents that are not well-formed Unicode to be
  parsed, if that is ever desirable. (Fixes issue #29)

[0.4.8.0] - 2021-05-21
----------------------

This is a major milestone for PyMD4C! Apart from a new, more object-oriented
API, the addition of a test suite means it is ready to come out of beta!

Some minor breaking changes were introduced. See the changes section below.
Not ideal, but better to do it now rather than after a stable release.

### Added

- Add a test suite (there is more to do here, but it's complete enough that I
  feel comfortable saying PyMD4C is no longer in beta)
- Object-oriented `ParserObject` API as an alternative to `GenericParser`
- `lookup_entity()` function for applications using `GenericParser` or
  `ParserObject` to translate HTML entities
- `DOMParser` for applications that require an AST (also serves as an example
  of using the object-oriented API)
  * This should be considered experimental for now. While it is well-tested, I
    am interested in feedback about the API, and I may make updates to the API
    based on that feedback.

### Changed

- Omit `info` and `lang` from indented code blocks, where they are not
  relevant.
- Keyword argument `permissive_auto_links` renamed to `permissive_autolinks`
  (for consistency with `permissive_url_autolinks`, `permissive_www_autolinks`,
  and `permissive_email_autolinks`).
- Moved main documentation from the README to a collection of Sphinx docs

### Fixed

- `GenericParser` now provides the correct details dict for tables

[0.4.7.0b1] - 2021-05-08
------------------------

### Added

- `GenericParser` provides details from `MD_BLOCK_TABLE_DETAIL`, introduced in
  the latest version of MD4C, when block callbacks are called for a table.

### Changed

- Compatible with MD4C version 0.4.7

### Fixed

- Typo for flag in README (PR #19, thanks @modeja)
- Parse unsigned ints in `MD_BLOCK_*_DETAIL` structs as unsigned instead of
  signed

[0.4.6.0b1] - 2020-10-28
------------------------

### Added

- Windows builds
- Keyword arguments for option flags for `GenericParser` and `HTMLRenderer`
  (Credit to @mondeja on GitHub for implementing)

### Changed

- Compatible with MD4C version 0.4.6
- Omit keys from the `details` dict when they are irrelevant: No `task_mark` or
  `task_mark_offset` for non-task-lists, no `fence_char` for indented code
  blocks. (Credit to @mondeja on GitHub for implementing)
- Use a bool for appropriate keys in `details`: `is_tight`, `is_task` (Credit
  to @mondeja on GitHub for implementing)

### Fixed

- No more segmentation fault in `GenericParser` when an `MD_ATTRIBUTE` is
  missing, e.g. info string for indented code blocks. (Thanks to @mondeja on
  GitHub for reporting)

[0.4.4.0b1] - 2020-06-16
------------------------

This is the initial beta release.

### Added

- `GenericParser` class wrapping the MD4C core parser
- `HTMLRenderer` class wrapping the MD4C HTML renderer
- Written for the MD4C version 0.4.4

[semver]: https://semver.org/
[pep440]: https://www.python.org/dev/peps/pep-0440/#version-scheme

[Unreleased]: https://github.com/dominickpastore/pymd4c/compare/v1.1.1..dev
[1.1.1]: https://github.com/dominickpastore/pymd4c/compare/tag/v1.1.0..v1.1.1
[1.1.0]: https://github.com/dominickpastore/pymd4c/compare/tag/v1.0.0..v1.1.0
[1.0.0]: https://github.com/dominickpastore/pymd4c/compare/tag/v0.4.8.0..v1.0.0
[0.4.8.0]: https://github.com/dominickpastore/pymd4c/compare/tag/v0.4.7.0b1..v0.4.8.0
[0.4.7.0b1]: https://github.com/dominickpastore/pymd4c/compare/tag/v0.4.6.0b1..v0.4.7.0b1
[0.4.6.0b1]: https://github.com/dominickpastore/pymd4c/compare/tag/release-0.4.4.0b1..v0.4.6.0b1
[0.4.4.0b1]: https://github.com/dominickpastore/pymd4c/releases/tag/release-0.4.4.0b1
