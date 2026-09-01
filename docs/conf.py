project = "phys240"
copyright = "PHYS 240"
author = "PHYS 240 course staff"

import os
import sys
sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "numpydoc",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "undoc-members": False}

# numpydoc's own cross-reference machinery is noisy for a single module;
# turn off the class-member table it generates and keep the plain sections.
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
numpydoc_validation_checks = set()

intersphinx_timeout = 10
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

# intersphinx is a network fetch; do not fail the build when it is
# unreachable (offline builds, flaky CI runners).
suppress_warnings = ["config.cache"]
nitpicky = False

html_theme = "furo"
html_title = "phys240"
