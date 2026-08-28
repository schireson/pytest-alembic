# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

import os
import sys

from sphinx_pyproject import SphinxConfig

sys.path.insert(0, os.path.abspath(".."))

_config = SphinxConfig("../../pyproject.toml", globalns=globals())
project = "Pytest Alembic"
version = _config.version
release = _config.version

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = [".rst", ".md"]

# quickstart.rst supplies the page's H1 and then includes README.md, whose own top
# level is `##`. That is the correct nesting for an included document, but myst-parser
# reports it as a document starting at H2, so the check is suppressed rather than
# renumbering the README's headings for the benefit of one include.
suppress_warnings = ["myst.header"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_sidebars = {"**": ["globaltoc.html", "relations.html", "sourcelink.html", "searchbox.html"]}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
    "alembic": ("https://alembic.sqlalchemy.org/en/latest/", None),
}

# Every unresolved cross-reference is a warning, and `make docs` builds under `-W`, so it
# is an error. Without this, sphinx silently drops an unresolved Python reference and
# renders the text unlinked.
nitpicky = True

autoclass_content = "both"
master_doc = "index"
