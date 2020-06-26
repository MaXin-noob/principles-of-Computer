# -*- coding: utf-8 -*-
"""
Distribution internals
======================

.. warning::

    This module is deprecated.

These are some distribution-related routines. It is doubtful that you would
ever need them unless you are developing Tool itself.
"""
def check_dependencies(module_name, attr_name=None):
    """
    Checks module or attribute dependencies. Raises NameError if setup.py does
    not specify dependencies for given module or attribute.

    :param module_name:
        e.g. "tool.ext.jinja"
    :param attr_name:
        e.g. "slugify_i18n" from "tool.ext.strings:slugify_i18n"

    """
    import warnings
    warnings.warn('tool.dist is deprecated; use ImportError '
                  'catching technique instead.')
