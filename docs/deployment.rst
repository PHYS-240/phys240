Deployment
==========

Where files go
--------------

``autotests.yml``
    Course root.  nbgrader looks first in the assignment's ``source/``
    directory, then falls back to a bare relative ``autotests.yml`` — which
    resolves against the current working directory.  **Always run nbgrader
    from the course root.**

``phys240.py``
    A copy in **every** assignment ``source/`` directory.  This is required,
    not belt-and-braces:

    * ``InstantiateTests`` starts its kernel with ``cwd`` set to the
      *notebook's* directory, so a course-root copy is not importable at
      generate time.  Without it, generation fails with a mangled traceback
      (``TypeError: __str__ returned non-string (type list)``) rather than a
      ``ModuleNotFoundError``.
    * ``generate_assignment`` copies it into ``release/``, so students get it.
    * ``autograde`` overwrites every non-``.ipynb`` file in a submission with
      the master from ``source/``.  That is what prevents a student from
      shadowing the module with a stub whose ``num()`` returns a constant —
      but only if a file of that name exists in ``source/``.

Installing it into the JupyterHub environment is convenient for interactive
use and does **not** substitute for the ``source/`` copy.

Instructor-only cells
---------------------

CoCalc's nbgrader has a "Remove" cell type that writes ``remove: true`` into
the cell metadata.  Upstream nbgrader has no such key, and its v3 schema sets
``additionalProperties: false``, so those cells fail ``CheckCellMetadata``.

``nbgrader update`` resolves the error by *deleting* the key, which for
``remove: true`` cells silently reverses the behaviour — they will be released
to students.  Run ``tools/audit_remove.py`` over ``source/`` first.

To reproduce the feature, tag the cell ``instructor-only`` and prepend
nbconvert's ``TagRemovePreprocessor``:

.. code-block:: python

   from nbconvert.preprocessors import TagRemovePreprocessor
   from nbgrader.converters.generate_assignment import GenerateAssignment

   c.TagRemovePreprocessor.remove_cell_tags = {"instructor-only"}
   c.TagRemovePreprocessor.enabled = True
   c.GenerateAssignment.preprocessors = (
       [TagRemovePreprocessor] + GenerateAssignment.preprocessors.default_args[0]
   )

It must run before ``ComputeChecksums`` and ``SaveCells``, or you will register
grade cells in the gradebook that do not exist in the released notebook.

Other gotchas
-------------

* Cells containing ``AUTOTEST`` must be marked as autograder test cells
  (``grade: true``) or generation raises rather than warns.
* Generation executes your solution in a live kernel, so it is slow and fails
  hard on a broken solution cell.
* A ``figures/`` directory left in ``source/`` from your own test run is copied
  into ``release/``.  Clean it before generating.
