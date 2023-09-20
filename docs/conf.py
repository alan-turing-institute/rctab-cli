"""Configuration file for the Sphinx documentation builder."""
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sphinx_rtd_theme

# pylint: disable=invalid-name

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "rctab-cli"
# pylint: disable=redefined-builtin
copyright = "2023, The Alan Turing Institute's Research Computing Team"
# pylint: enable=redefined-builtin
author = "The Alan Turing Institute's Research Computing Team"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

release = "0.1"
version = "0.1.0"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    #    "subprojecttoctree",
]

intersphinx_disabled_domains = ["std"]

# We recommend adding the following config value.
# Sphinx defaults to automatically resolve *unresolved* labels using all your Intersphinx mappings.
# This behavior has unintended side-effects, namely that documentations local references can
# suddenly resolve to an external location.
# See also:
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_disabled_reftypes
intersphinx_disabled_reftypes = ["*"]

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ["_static"]

html_logo = "RCTab-hex.png"


def setup(app):  # type: ignore
    """Tasks to perform during app setup."""
    app.add_css_file("css/custom.css")


# -- Options for EPUB output

epub_show_urls = "footnote"

# -- Options for Subprojecttoctree

# is_subproject = True
# readthedocs_url = "https://rctab.readthedocs.io"

# -- Options for autosummary extension

autosummary_generate = True
