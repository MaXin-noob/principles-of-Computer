# -*- coding: utf-8 -*-
"""
String utilities
================

:state: stable
:dependencies: `Unidecode`_ (optional)

.. _Unidecode: http://pypi.python.org/pypi/Unidecode

"""

__all__ = ['slugify', 'slugify_i18n']

import re
try:
    from unidecode import unidecode
except ImportError:  # pragma: nocover
    unidecode = None


SLUG_RE = re.compile(r'[^\w\s\-]')

def _slugify_simple(value):
    return unicode(SLUG_RE.sub('',value).strip()[:20].lower().replace(' ','-'))

def slugify(value):
    """
    If `Unidecode`_ is available, calls :func:`slugify_i18n`. If not, parses
    the value with a latin-only regular expression, i.e. may return empty or
    otherwise useless strings for non-latin strings. Usage::

        >>> slugify(u'Foo? bar! 123...')
        u'foo-bar-123'

    """
    if unidecode:
        return slugify_i18n(value)
    return _slugify_simple(value)  # pragma: nocover

def slugify_i18n(value):
    """
    Transliterates given string with `Unidecode`_ and returns its "slugified"
    version. Usage::

        >>> slugify(u'Foo? Привет! 123')
        u'foo-privet-123'

    """
    if unidecode is None:  # pragma: nocover
        raise ImportError('Could not load library "unidecode".')
    return _slugify_simple(unidecode(value))
