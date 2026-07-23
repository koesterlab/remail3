import os
import sys

sys.path.insert(0, os.path.abspath("."))


project = "remail3"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "myst_parser",  # For markdown support
]

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
}

html_favicon = "favicon.png"

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"

include_patterns = [
    "docs/**/*.md",
    "docs/**/*.rst",
    "index.rst",
]


autodoc_default_options = {
    "member-order": "bysource",
}

autodoc_inherit_docstrings = False

suppress_warnings = ["ref.python"]
