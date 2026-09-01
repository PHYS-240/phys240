"""phys240.py -- shared course utilities for PHYS 240 (Computational Physics).

One flat module, four jobs:

  1. NORMALIZATION  -- helpers used by ``### AUTOTEST`` directives via
     ``autotests.yml``.  Everything returns a ``Tag``.
  2. DOCSTRINGS     -- a minimal numpydoc conformance check.
  3. FIGURES        -- standard figure saving and the end-of-set portfolio.
  4. ASSERTIONS     -- drop-in replacements for the ``nose.tools`` names used
     throughout the existing problem sets.  nose is dead on Python 3.10+
     (it imports the removed ``imp`` module), so every legacy
     ``from nose.tools import assert_equal`` must become
     ``from phys240 import assert_equal``.

Deployment
----------
Install into the JupyterHub environment for interactive convenience, AND keep
a copy in each assignment's ``source/`` directory.  The second copy is the
part that matters for integrity: a local ``phys240.py`` in a student's
directory would shadow the installed package, and ``nbgrader autograde``
only overwrites a shadowing file if a master by that name exists in
``source/``.

Optional dependencies are imported lazily: numpy (normalization, figures),
numpydoc (docstring checks), matplotlib and pypdf (figures).
"""

import hashlib
import inspect
import math
import os
import re
import unittest

__all__ = [
    # normalization
    "Tag", "num", "cnum", "kind", "seq", "bag", "shape", "stats", "arr",
    "close", "keys", "mapping", "raises", "signature", "attrs",
    "nlines", "linedata", "labeled", "limits",
    # docstrings
    "BASIC_CHECKS", "check_docstring", "docstring", "assert_docstring",
    # figures
    "figure_path", "save_figure", "has_figure", "assert_figure",
    "build_portfolio", "assert_portfolio",
    # assertions
    "assert_equal", "assert_not_equal", "assert_almost_equal",
    "assert_not_almost_equal", "assert_true", "assert_false", "assert_is",
    "assert_is_not", "assert_is_none", "assert_is_not_none", "assert_in",
    "assert_not_in", "assert_is_instance", "assert_greater", "assert_less",
    "assert_greater_equal", "assert_less_equal", "assert_list_equal",
    "assert_dict_equal", "assert_tuple_equal", "assert_set_equal",
    "assert_sequence_equal", "assert_raises", "assert_count_equal",
    "assert_allclose",
]


# ======================================================================
# 1. NORMALIZATION -- used by autotests.yml
# ======================================================================

class Tag(str):
    """A normalized, single-line, quote-free test value.

    Its dispatch key in ``autotests.yml`` is ``phys240.Tag``, which comes
    from ``__module__``.  If this module is ever renamed or split into a
    package, pin the key with ``Tag.__module__ = "phys240"`` or the YAML
    template will silently stop matching and fall through to ``default``.
    """

    __slots__ = ()

    def __repr__(self):
        return str.__str__(self)


def _f(x, sig):
    """Format a real number to `sig` significant digits, scale-free."""
    x = float(x)
    if math.isnan(x):
        return "nan"
    if math.isinf(x):
        return "inf" if x > 0 else "-inf"
    if x == 0.0:
        return "0." + "0" * (sig - 1) + "e+00"      # collapses -0.0
    return f"{x:.{sig - 1}e}"


def num(x, sig=6):
    """Canonical form of any real scalar: int, float, np.float64, ...

    Deliberately type-agnostic, so a student returning np.float64 where the
    solution returned float still passes the *value* test.  Use kind() to
    test the type separately.
    """
    return Tag("num " + _f(x, sig))


def cnum(z, sig=6):
    """Canonical form of a complex scalar."""
    z = complex(z)
    return Tag("cnum " + _f(z.real, sig) + " " + _f(z.imag, sig))


def kind(x):
    """Coarse type category: number, bool, string, array, sequence, ...

    Use instead of type() to reject a wrong *category* without punishing
    int-vs-np.int64.
    """
    if isinstance(x, bool):
        return Tag("kind bool")
    try:
        import numpy as np
        if isinstance(x, np.bool_):
            return Tag("kind bool")
        if isinstance(x, np.ndarray):
            return Tag("kind array")
        if isinstance(x, np.number):
            return Tag("kind number")
    except ImportError:
        pass
    if isinstance(x, (int, float)):
        return Tag("kind number")
    if isinstance(x, complex):
        return Tag("kind complex")
    if isinstance(x, str):
        return Tag("kind string")
    if isinstance(x, dict):
        return Tag("kind mapping")
    if isinstance(x, (set, frozenset)):
        return Tag("kind set")
    if isinstance(x, (list, tuple)):
        return Tag("kind sequence")
    if x is None:
        return Tag("kind none")
    if callable(x):
        return Tag("kind callable")
    return Tag("kind " + type(x).__name__)


def _elem(e, sig):
    if isinstance(e, bool):
        return str(e)
    if isinstance(e, (int, float)):
        return _f(e, sig)
    if isinstance(e, complex):
        return _f(e.real, sig) + "j" + _f(e.imag, sig)
    try:
        import numpy as np
        if isinstance(e, np.bool_):
            return str(bool(e))
        if isinstance(e, np.number):
            return _f(e, sig)
        if isinstance(e, np.ndarray):
            return str(arr(e, sig))
    except ImportError:
        pass
    return str(e)


def seq(s, sig=6):
    """Canonical form of a list/tuple, elementwise, order-sensitive."""
    return Tag("seq " + " ".join(_elem(e, sig) for e in s))


def bag(s, sig=6):
    """Canonical form of a list/tuple/set, order-INsensitive."""
    return Tag("bag " + " ".join(sorted(_elem(e, sig) for e in s)))


def shape(a):
    """Shape and dtype kind of an array (or length of a sequence)."""
    try:
        import numpy as np
        a = np.asarray(a)
        return Tag(f"shape {a.shape} {a.dtype.kind}")
    except ImportError:
        return Tag(f"shape ({len(a)},) ?")


def stats(a, sig=4):
    """Min / max / mean / std of an array, at reduced precision.

    Cheap partial credit: catches sign errors, wrong grid endpoints and bad
    normalizations without demanding the full array match.
    """
    import numpy as np
    a = np.asarray(a, dtype=float).ravel()
    if a.size == 0:
        return Tag("stats empty")
    return Tag("stats " + " ".join(
        _f(v, sig) for v in (a.min(), a.max(), a.mean(), a.std())))


def arr(a, sig=6):
    """Full-content checksum of an array.

    Returns a short digest rather than the array itself, so even a
    non-hashed AUTOTEST stays a one-liner instead of pasting 1000 numbers
    into the student notebook.  Immune to numpy print options.
    """
    import numpy as np
    a = np.asarray(a)
    if a.dtype.kind == "f":
        body = " ".join(_f(v, sig) for v in a.ravel())
    elif a.dtype.kind == "c":
        body = " ".join(_f(v.real, sig) + "j" + _f(v.imag, sig)
                        for v in a.ravel())
    else:
        body = " ".join(str(v) for v in a.ravel().tolist())
    payload = f"{a.shape}|{a.dtype.kind}|{body}"
    return Tag("arr " + hashlib.sha256(payload.encode()).hexdigest()[:16])


def close(a, b, rtol=1e-5, atol=1e-8):
    """Tolerance check, for when significant figures are too rigid.

    Use in a directive when the quantity is genuinely noisy (Monte Carlo,
    iterative solvers)::

        ### AUTOTEST p240.close(estimate_pi(10**6), 3.14159, rtol=1e-2)
    """
    import numpy as np
    return Tag("close " + str(bool(np.allclose(a, b, rtol=rtol, atol=atol))))


def keys(d):
    """Sorted keys of a mapping."""
    return Tag("keys " + " ".join(sorted(map(str, d.keys()))))


def mapping(d, sig=6):
    """Canonical key-value form of a mapping."""
    items = sorted((str(k), _elem(v, sig)) for k, v in d.items())
    return Tag("map " + " ".join(f"{k}={v}" for k, v in items))


def raises(fn, *args, **kwargs):
    """Name of the exception ``fn(*args)`` raises, or 'None'.

    The autotest replacement for ``assert_raises``::

        ### AUTOTEST p240.raises(get_resistor_value, ['bl', 'bl'])
    """
    try:
        fn(*args, **kwargs)
    except BaseException as exc:
        return Tag("raises " + type(exc).__name__)
    return Tag("raises None")


def signature(fn):
    """Parameter names and defaults of a function.

    Catches renamed or reordered parameters, which silently break keyword
    calls later in the assignment.
    """
    parts = []
    for name, p in inspect.signature(fn).parameters.items():
        d = "" if p.default is inspect.Parameter.empty else f"={p.default!r}"
        parts.append(f"{name}{d}")
    return Tag("sig " + " ".join(parts))


def attrs(obj, *names):
    """Presence and coarse type of named attributes/methods on an object.

    For custom classes (the Vector class in ps10, say)::

        ### AUTOTEST p240.attrs(Vector(1,2,3), 'x', 'mag', 'dot', 'cross')
    """
    out = []
    for n in names:
        if not hasattr(obj, n):
            out.append(f"{n}=MISSING")
        else:
            v = getattr(obj, n)
            out.append(f"{n}=callable" if callable(v)
                       else f"{n}={str(kind(v))[5:]}")
    return Tag("attrs " + " ".join(out))


# --- matplotlib -------------------------------------------------------

def nlines(ax):
    """Number of Line2D objects on an Axes."""
    return Tag(f"nlines {len(ax.get_lines())}")


def linedata(ax, sig=4):
    """Checksum of every line's x and y data on an Axes."""
    parts = []
    for ln in ax.get_lines():
        parts.append(str(arr(ln.get_xdata(), sig)))
        parts.append(str(arr(ln.get_ydata(), sig)))
    return Tag("linedata "
               + hashlib.sha256("|".join(parts).encode()).hexdigest()[:16])


def labeled(ax):
    """Whether the axes have a non-empty x label, y label, and title.

    Checks that labels EXIST rather than matching their text, so students
    are not punished for wording.
    """
    return Tag("labeled "
               + str(bool(ax.get_xlabel().strip()))
               + " " + str(bool(ax.get_ylabel().strip()))
               + " " + str(bool(ax.get_title().strip())))


def limits(ax, sig=3):
    """Axis limits at reduced precision."""
    return Tag("limits " + " ".join(
        _f(v, sig) for v in (*ax.get_xlim(), *ax.get_ylim())))


# ======================================================================
# 2. DOCSTRINGS -- minimal numpydoc conformance
# ======================================================================

# GL08 - no docstring at all
# SS01 - no one-line summary
# PR01 - a parameter in the signature is not documented
# PR02 - a documented parameter does not exist in the signature
# RT01 - no Returns section (only fires if the function returns something)
BASIC_CHECKS = {"GL08", "SS01", "PR01", "PR02", "RT01"}


def check_docstring(func, require_raises=False):
    """Check a function's docstring against the basic numpydoc subset.

    Ignores numpydoc's pedantic checks (Examples, See Also, extended
    summary, capitalization) -- those are not worth failing a problem set
    over, and are better raised in an interview.

    Parameters
    ----------
    func : callable
        A live function object; works on functions defined in a notebook
        cell, no import path needed.
    require_raises : bool, optional
        Also require a non-empty Raises section.  Use only where the prompt
        explicitly asks students to document an exception; numpydoc's own
        validator never emits an error for Raises.

    Returns
    -------
    list of str
        Human-readable problems.  Empty means the docstring passes.
    """
    from numpydoc.docscrape import get_doc_object
    from numpydoc.validate import validate

    doc_object = get_doc_object(func)
    try:
        result = validate(doc_object)
        problems = [msg for code, msg in result["errors"]
                    if code in BASIC_CHECKS]
    except OSError:
        # Source was not retrievable (function built via exec() rather than
        # a normal def), so the source-introspecting RT01 check cannot run.
        problems = []
        if not doc_object["Summary"]:
            problems.append("No summary found.")
        missing = set(inspect.signature(func).parameters) - {
            p.name for p in doc_object["Parameters"]}
        if missing:
            problems.append(f"Parameters {sorted(missing)} not documented.")

    if require_raises and not doc_object["Raises"]:
        problems.append(
            "No Raises section found (this problem requires documenting "
            "the exception(s) your function raises).")

    return problems


def docstring(func, require_raises=False):
    """Docstring conformance as a normalized Tag, for ``### AUTOTEST``.

    Prefer assert_docstring() in most cases: its message names the specific
    problem, and unlike a physics answer there is no reason to hide from a
    student that their Returns section is missing.
    """
    problems = check_docstring(func, require_raises=require_raises)
    return Tag("docstring " + ("ok" if not problems else str(len(problems))))


def assert_docstring(func, require_raises=False):
    """Assert that a function's docstring meets the basic numpydoc subset."""
    problems = check_docstring(func, require_raises=require_raises)
    assert not problems, (
        f"The docstring for `{func.__name__}` does not meet the course's "
        f"numpydoc requirements:\n  - " + "\n  - ".join(problems))


# ======================================================================
# 3. FIGURES -- standard saving and the end-of-set portfolio
# ======================================================================

FIGURE_DIR = "figures"
MIN_FIGURE_BYTES = 2000


def figure_path(n, directory=FIGURE_DIR):
    """Canonical path for the figure belonging to problem `n`."""
    return os.path.join(directory, f"problem{int(n)}.pdf")


def save_figure(fig, n, directory=FIGURE_DIR, **kwargs):
    """Save a figure to the standard location for problem `n`.

    Creates the directory if needed and defaults to a tight bounding box so
    the compiled portfolio is visually consistent.

    Returns
    -------
    str
        The path written.
    """
    os.makedirs(directory, exist_ok=True)
    kwargs.setdefault("bbox_inches", "tight")
    path = figure_path(n, directory)
    fig.savefig(path, **kwargs)
    return path


def has_figure(n, directory=FIGURE_DIR, min_bytes=MIN_FIGURE_BYTES):
    """Whether problem `n`'s figure exists and is not a blank canvas."""
    path = figure_path(n, directory)
    ok = os.path.exists(path) and os.path.getsize(path) >= min_bytes
    return Tag("figure " + str(bool(ok)))


def assert_figure(n, directory=FIGURE_DIR, min_bytes=MIN_FIGURE_BYTES):
    """Assert that problem `n`'s figure was written and is non-trivial."""
    path = figure_path(n, directory)
    assert os.path.exists(path), (
        f"Expected to find `{path}`, but it does not exist. Save your figure "
        f"with p240.save_figure(fig, {n}).")
    size = os.path.getsize(path)
    assert size >= min_bytes, (
        f"`{path}` exists but is only {size} bytes, which suggests an empty "
        f"canvas. Did you call save_figure before plotting anything?")


def _natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def build_portfolio(expected=None, directory=FIGURE_DIR,
                    out="portfolio.pdf"):
    """Concatenate this problem set's figures into one PDF.

    Parameters
    ----------
    expected : iterable of int, optional
        Problem numbers that should be present.  If given, pages appear in
        this order and gaps are reported; if omitted, every
        ``problemN.pdf`` in `directory` is used in natural numeric order.
    directory : str, optional
        Where the figures live.
    out : str, optional
        Output filename, written inside `directory`.

    Returns
    -------
    list of int or list of str
        The problems that were missing.  Empty means the portfolio is
        complete.  Missing figures are skipped rather than raising, so one
        unattempted problem does not destroy the whole portfolio.
    """
    from pypdf import PdfWriter

    os.makedirs(directory, exist_ok=True)
    if expected is None:
        import glob
        paths = sorted(glob.glob(os.path.join(directory, "problem*.pdf")),
                       key=_natural_key)
        candidates = [(os.path.basename(p), p) for p in paths]
    else:
        candidates = [(n, figure_path(n, directory)) for n in expected]

    missing = []
    writer = PdfWriter()
    for label, path in candidates:
        if not os.path.exists(path):
            missing.append(label)
            continue
        try:
            writer.append(path)
        except Exception:
            missing.append(label)

    out_path = os.path.join(directory, out)
    with open(out_path, "wb") as fh:
        writer.write(fh)

    if missing:
        print(f"Wrote {out_path}, but these problems had no usable figure: "
              f"{missing}")
    else:
        print(f"Wrote {out_path} with {len(candidates)} figures.")
    return missing


def assert_portfolio(directory=FIGURE_DIR, out="portfolio.pdf",
                     min_bytes=MIN_FIGURE_BYTES):
    """Assert that the compiled portfolio exists and is non-trivial."""
    path = os.path.join(directory, out)
    assert os.path.exists(path), (
        f"Expected `{path}`. Run the portfolio cell at the end of the "
        f"notebook before submitting.")
    assert os.path.getsize(path) >= min_bytes, (
        f"`{path}` is suspiciously small; it may contain no pages.")


# ======================================================================
# 4. ASSERTIONS -- replacements for the dead nose.tools names
# ======================================================================
#
# nose has been unmaintained for years and cannot be imported on Python
# 3.10+ (it uses the removed `imp` module).  These are bound from a
# unittest.TestCase instance, which is exactly how nose.tools built them,
# so signatures and messages are unchanged: places=, delta=, msg= all work.

_tc = unittest.TestCase()
_tc.maxDiff = None
_tc.longMessage = True

assert_equal = _tc.assertEqual
assert_not_equal = _tc.assertNotEqual
assert_almost_equal = _tc.assertAlmostEqual
assert_not_almost_equal = _tc.assertNotAlmostEqual
assert_true = _tc.assertTrue
assert_false = _tc.assertFalse
assert_is = _tc.assertIs
assert_is_not = _tc.assertIsNot
assert_is_none = _tc.assertIsNone
assert_is_not_none = _tc.assertIsNotNone
assert_in = _tc.assertIn
assert_not_in = _tc.assertNotIn
assert_is_instance = _tc.assertIsInstance
assert_greater = _tc.assertGreater
assert_less = _tc.assertLess
assert_greater_equal = _tc.assertGreaterEqual
assert_less_equal = _tc.assertLessEqual
assert_list_equal = _tc.assertListEqual
assert_dict_equal = _tc.assertDictEqual
assert_tuple_equal = _tc.assertTupleEqual
assert_set_equal = _tc.assertSetEqual
assert_sequence_equal = _tc.assertSequenceEqual
assert_count_equal = _tc.assertCountEqual
assert_raises = _tc.assertRaises


def assert_allclose(actual, desired, rtol=1e-7, atol=0, msg=None):
    """Array-aware near-equality, since assert_almost_equal is scalar-only.

    Use this in place of looping assert_almost_equal over array elements.
    """
    import numpy as np
    np.testing.assert_allclose(actual, desired, rtol=rtol, atol=atol,
                               err_msg=msg or "")
