# phys240 — working notes for Claude Code

Shared testing/utility module for PHYS 240 (Computational Physics), used by
nbgrader's `### AUTOTEST` machinery and by hand-written test cells.

## Ground rules

**Normalization output is a public contract.** Every `phys240.Tag` value from
`num`, `arr`, `seq`, `shape`, `stats`, `kind`, `raises`, etc. is SHA-256'd and
baked into released student notebooks. Changing a separator, a format spec, or
a prefix silently invalidates every assignment already distributed. Treat
`tests/test_phys240.py::test_golden_values` as a tripwire: if you have to
change it, that is a breaking change and needs a version bump plus
regeneration of every affected assignment.

**`Tag.__module__` must stay `"phys240"`.** `autotests.yml` keys its
single-line template on the dispatch name `phys240.Tag`. If this module is ever
split into a package, the key becomes `phys240.normalize.Tag`, nothing matches,
and every explicit `p240.num(...)` directive falls through to the `default`
template — producing tests that pass while checking the wrong thing. Pin it
explicitly if the layout changes.

**Keep it one flat module.** Deliberate: a copy has to be dropped into every
nbgrader assignment `source/` directory, and a single file is much easier to
keep in sync than a package tree.

**Optional deps stay lazy.** numpy, numpydoc, matplotlib, and pypdf are all
imported inside the functions that need them. Students' kernels may not have
all of them, and `phys240` must import cleanly regardless.

## Current known task

26 functions fail `check_docstring` — the module does not satisfy the numpydoc
standard it enforces. Failures are almost all missing `Parameters` and
`Returns` sections (descriptions are currently written as prose). Fixing them
makes CI green and is also the first real test of the checker against a
non-trivial corpus. Run `pytest -q` to see the list.

Docstrings are for instructors and TAs, not students. Be technical and terse.

## Layout

    phys240.py                 the module (flat, deliberately)
    autotests.yml              nbgrader test templates; keys must match phys240 helpers
    tools/audit_remove.py      finds CoCalc `remove` metadata before `nbgrader update`
    docs/                      Sphinx; deployed to Pages by .github/workflows/docs.yml
    tests/                     pytest; determinism + golden values + docstring dogfooding

## Deployment reminder

`autotests.yml` lives in the course root. `phys240.py` must be copied into
*every* assignment `source/` directory — not just the course root — because
`InstantiateTests` runs its kernel with cwd set to the notebook's directory,
and because `autograde`'s source-overwrite is what stops students shadowing the
module with a stub. See `docs/deployment.rst`.
