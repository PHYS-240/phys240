"""Tests for phys240.

The determinism tests matter more than they look: every hash baked into every
released notebook depends on these functions producing byte-identical output.
A well-meaning refactor that changes a separator or a format spec silently
invalidates every assignment already in students' hands.
"""

import inspect

import numpy as np
import pytest

import phys240 as p240


# --- determinism / stability -----------------------------------------

def test_num_is_scale_free():
    assert p240.num(0.1 + 0.2, 6) == p240.num(0.3, 6)
    assert p240.num(1e-12, 3) != p240.num(2e-12, 3)
    assert p240.num(6.1e8, 3) != p240.num(6.2e8, 3)


def test_num_is_type_agnostic():
    assert p240.num(2.5) == p240.num(np.float64(2.5))
    assert p240.num(3) == p240.num(np.int64(3))


def test_negative_zero_collapses():
    assert p240.num(-0.0) == p240.num(0.0)


def test_bool_and_int_differ():
    assert p240.kind(True) != p240.kind(1)


def test_arr_ignores_print_options():
    a = np.linspace(0, 1, 2000)
    before = p240.arr(a)
    np.set_printoptions(precision=2, linewidth=40, threshold=10)
    try:
        assert p240.arr(a) == before
    finally:
        np.set_printoptions()


def test_arr_distinguishes_shape():
    assert p240.arr(np.zeros((2, 3))) != p240.arr(np.zeros((3, 2)))


def test_seq_and_bag():
    assert p240.seq([1, 2]) != p240.seq([2, 1])
    assert p240.bag([1, 2]) == p240.bag([2, 1])


def test_golden_values():
    """Pin exact output. Changing these invalidates released notebooks."""
    assert str(p240.num(1 / 3, 4)) == "num 3.333e-01"
    assert str(p240.kind(np.zeros(3))) == "kind array"
    assert str(p240.shape(np.zeros((2, 3)))) == "shape (2, 3) f"


def test_raises_reports_exception_type():
    def boom(x):
        raise ValueError("no")
    assert str(p240.raises(boom, 1)) == "raises ValueError"
    assert str(p240.raises(lambda: 1)) == "raises None"


def test_tag_dispatch_key():
    """autotests.yml keys the Tag template on this exact name."""
    assert p240.Tag.__module__ == "phys240"


# --- docstring checker ------------------------------------------------

def test_docstring_checker_catches_missing_param():
    def f(x, y):
        """
        Add.

        Parameters
        ----------
        x : int
            A value.

        Returns
        -------
        int
            Sum.
        """
        return x + y
    assert p240.check_docstring(f)


def test_docstring_checker_passes_good_docstring():
    def f(x):
        """
        Square a number.

        Parameters
        ----------
        x : int
            A value.

        Returns
        -------
        int
            The square.
        """
        return x * x
    assert p240.check_docstring(f) == []


@pytest.mark.parametrize("name", [
    n for n in p240.__all__
    if inspect.isfunction(getattr(p240, n))
    and getattr(p240, n).__module__ == "phys240"
])
def test_module_passes_its_own_docstring_check(name):
    """Dogfooding: phys240 must satisfy the standard it enforces."""
    problems = p240.check_docstring(getattr(p240, name))
    assert not problems, f"{name}: " + "; ".join(problems)
