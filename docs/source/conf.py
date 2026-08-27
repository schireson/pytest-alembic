# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Pytest Alembic"
release = "0.4.0"
version = "0.4.0"

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
    # 2.0, not the 1.3 this pointed at for years. The project supports sqlalchemy
    # >= 1.4 and the CI matrix runs 2.0.x, so the 1.3 inventory sent readers to
    # documentation for a version pytest-alembic no longer works with -- and
    # `sqlalchemy.ext.asyncio` does not exist in it at all, so the AsyncEngine
    # reference on the asyncio page silently rendered as unlinked text.
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
}

autoclass_content = "both"
master_doc = "index"
