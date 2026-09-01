Overview
========

``phys240.py`` is a single flat module with four responsibilities.

Normalization
-------------

Helpers used by ``### AUTOTEST`` directives, via ``autotests.yml``.  Every one
returns a :class:`phys240.Tag`, a ``str`` subclass whose dispatch key is
``phys240.Tag``.

The reason these exist rather than doing the work in Jinja: nbgrader's default
templates normalize floats with ``round(x, 2)`` (decimal places, not
significant figures, so ``0.3989...`` becomes ``0.4``) and arrays with
``str(x)`` (sensitive to student-mutable ``numpy`` print options, and
ellipsis-truncated past 1000 elements).  Doing it in Python makes the
normalization scale-free and deterministic.

Docstrings
----------

A deliberately minimal numpydoc conformance check: summary, ``Parameters``
matching the signature, ``Returns`` when the function returns something, and
optionally ``Raises``.  numpydoc's full check suite is far too pedantic for
first-time programmers.

Figures
-------

Standard figure paths, saving, presence checks, and the end-of-set portfolio
concatenation.

Assertions
----------

Replacements for the ``nose.tools`` names used throughout the legacy problem
sets.  ``nose`` cannot be imported on Python 3.10+ (it imports the removed
``imp`` module), so every ``from nose.tools import ...`` must become
``from phys240 import ...``.  These are bound from a ``unittest.TestCase``
instance, exactly as ``nose.tools`` did, so signatures and messages are
unchanged.
