Writing autotests
=================

How generation works
--------------------

A directive in an **Autograder tests** cell::

    ### AUTOTEST area
    ### HASHED AUTOTEST p240.num(area, 3)

is expanded by nbgrader's ``InstantiateTests`` preprocessor at
``generate_assignment`` time:

1. **dispatch** — ``type(snippet)`` is evaluated in a live kernel against
   *your solution*, and its IPython pretty name selects a template.
2. **test** — each ``test`` expression in that template wraps the snippet.
3. **normalize** — the result is passed through ``str(...)``.
4. **hash** — if ``HASHED``, the normalized value is SHA-256'd with a salt.
5. **check** — an ``assert`` is written into the released notebook.

Two consequences that surprise people:

*Dispatch runs against the solution, not the student.*  The template is chosen
by the type of the correct answer and then frozen.  This is why the value
tests go through type-agnostic helpers such as :func:`phys240.num` — a student
returning ``np.float64`` where the solution returned ``float`` should not fail
a physics test on a type technicality.

*Dispatch keys are IPython pretty names.*  Not ``str(type(x))``.  An array is
``numpy.ndarray``, a scalar is ``numpy.float64``, a class defined in a notebook
cell is ``__main__.Vector``, an axes object is
``matplotlib.axes._axes.Axes``.

Staged tests
------------

The first failing assert stops the cell, so template order determines which
message a student sees.  Order coarse to fine.  For arrays: kind, then
shape and dtype, then reduced-precision summary statistics, then the full
checksum — so "your grid endpoints are wrong" surfaces before "element 400
differs in the sixth digit".

When to hash
------------

Hashing is a deterrent, not a lock.  The salt is a short hex value sitting in
plain sight next to the digest, so a student who wants to invert a test only
needs the answer space to be small.  It works well for floats and arrays and
poorly for booleans, small integers, and short strings.  Prefer "compute this
quantity" over "is this stable, True or False?".

Do **not** hash docstring or figure checks.  There is no reason to hide from a
student that their ``Returns`` section is missing; use
:func:`phys240.assert_docstring` and unhashed ``### AUTOTEST p240.has_figure(1)``.

Escape hatches
--------------

When a type template's precision is wrong for one quantity, call the helper
explicitly::

    ### HASHED AUTOTEST p240.num(area, 3)
    ### AUTOTEST p240.close(estimate_pi(10**6), 3.14159, rtol=1e-2)

Use :func:`phys240.close` for genuinely noisy quantities — Monte Carlo,
iterative solvers with a tolerance — where hashing an exact value is hopeless.

Exception testing
-----------------

There is no autotest equivalent of ``assert_raises``.  Use
:func:`phys240.raises`, which returns the exception's type name::

    ### AUTOTEST p240.raises(get_resistor_value, ['bl', 'bl'])

Verifying an assignment
-----------------------

You cannot check a hashed test by reading it, and you cannot run the released
notebook (``ClearSolutions`` has replaced the answer with
``raise NotImplementedError()``, so it dies on the first test with a
``NameError``).  Formgrader's preview button is only a file-browser link to
``release/``.

The workflow that actually verifies:

.. code-block:: console

   $ nbgrader generate_assignment ps07 --source_with_tests --force
   $ nbgrader validate source_with_tests/ps07/ps07.ipynb   # positive control

Then the negative control, which matters more here than with plaintext tests:
a vacuous hashed test looks identical to a correct one.  Copy
``source_with_tests/``, perturb the solution, revalidate, and confirm both
that the test fires and that the *right* staged test fires.
