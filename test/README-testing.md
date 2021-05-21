Some Notes on Testing
=====================

Specification files
-------------------

Specifications and sample test cases reside in the `specs/` directory.

### `spec.txt`

From vanilla CommonMark.

### `gfm.txt`

Spec and test cases for GitHub Flavored Markdown. This contains just GitHub's
extensions. Unfortunately, there's no easy way to get them separate from the
main spec. (There is a file in their `cmark-gfm` repository,
`test/extensions.txt`, but it's very out of date.) The only way to get this
seems to be to open the full spec and pull out the sections for GitHub
extensions. A nontrivial amount of work, unfortunately.

Why not just use GitHub's `spec.txt` as an overall starting point? Because it's
missing some test cases from CommonMark's `spec.txt`, for some reason.
