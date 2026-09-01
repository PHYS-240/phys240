# phys240

Shared testing and course utilities for **PHYS 240: Computational Physics**.

Documentation: https://phys-240.github.io/phys240/

## What's here

| Path | Purpose |
| --- | --- |
| `phys240.py` | The module: autotest normalization, numpydoc checks, figure helpers, `nose.tools` replacements |
| `autotests.yml` | nbgrader test-generation templates, keyed to the types used in this course |
| `tools/audit_remove.py` | Finds CoCalc `remove` cell metadata before running `nbgrader update` |
| `docs/` | Sphinx sources (instructor-facing) |
| `tests/` | pytest suite, including determinism and golden-value tripwires |

## Quick start for a new instructor

1. `pip install -e .` into the JupyterHub environment.
2. Put `autotests.yml` in the course root. Always run nbgrader from there.
3. Put a copy of `phys240.py` in **every** assignment `source/` directory.
   This is required — see `docs/deployment.rst` for why a course-root copy
   is not enough.
4. Write test cells with `### AUTOTEST` / `### HASHED AUTOTEST` directives.
5. Verify with `--source_with_tests` plus a deliberate perturbation. A vacuous
   hashed test is indistinguishable from a correct one by inspection.

## Compatibility note

The legacy problem sets import from `nose.tools`, which cannot be imported on
Python 3.10+. Replace those imports with `from phys240 import ...`; the names
and signatures are unchanged.
