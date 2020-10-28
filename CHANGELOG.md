PyMD4C Changelog
================

PyMD4C version numbers track MD4C version numbers:

    Major.Minor.Patch.PyMD4C

* Major, minor, and patch versions match the version of MD4C that PyMD4C is
  based on.
* The final number is the PyMD4C version, which will start at zero for each
  MD4C version and be incremented each time there is a new PyMD4C release for
  the same version of MD4C.

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

[Unreleased]: https://github.com/dominickpastore/pymd4c/compare/v0.4.6.0b1..dev
[0.4.6.0b1]: https://github.com/dominickpastore/pymd4c/compare/tag/release-0.4.4.0b1..v0.4.6.0b1
[0.4.4.0b1]: https://github.com/dominickpastore/pymd4c/releases/tag/release-0.4.4.0b1
