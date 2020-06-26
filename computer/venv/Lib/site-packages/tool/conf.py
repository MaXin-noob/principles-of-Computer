# -*- coding: utf-8 -*-

"""
Configuration
=============

The configuration is just a dictionary. It may come from different sources and
in different formats, so we just provide some shortcuts to simplify things.



Sections
--------

The configuration can be empty or contain any of these values:

:bundles:
    a dictionary where keys are module paths and values are whatever these
    modules expect as settings. It is generally OK to pass `None` as the value
    when you only need to import the module. The module can then automatically
    subscribe to desired :doc:`signals`. Please refer to there modules'
    documentation for details. A number of such modules ships with Tool as
    :doc:`ext`.
:debug:
    if True, the WSGI application is wrapped in DebugMiddleware.

API reference
-------------
"""

from copy import deepcopy
import os.path
from tool.importing import import_attribute

__all__ = ['ConfigurationError', 'get_settings_for_bundle', 'load']


FORMATS = {
    'yaml': 'yaml.load',
    'json': 'json.loads',
}


class ConfigurationError(Exception):
    pass


def load(path, format=None):
    """
    Expects a filename, returns a dictionary. Raises ConfigurationError if
    the file could not be read or parsed.

    :param path:
        path to the file.
    :param format:
        format in which the configuration dictionary in serialized in the file
        (one of: "yaml", "json").

    """
    if not os.path.exists(path):
        raise ConfigurationError('File "%s" does not exist' % path)

    # guess file format
    if not format:
        for known_format in FORMATS:
            if path.endswith('.%s' % known_format):
                format = known_format
                break
        else:
            raise ConfigurationError('Could not guess format for "%s"' % path)
    assert format in FORMATS, 'unknown format %s' % format

    # deserialize file contents to a Python dictionary
    try:
        f = open(path)
    except IOError as e:
        raise ConfigurationError('Could not open "%s": %s' % (path, e))
    data = f.read()
    try:
        loader = import_attribute(FORMATS[format])
    except ImportError as e:
        raise ConfigurationError('Could not import "%s" format loader: %s'
                                 % (format, e))
    try:
        conf = loader(data)
    except Exception as e:
        raise ConfigurationError('Could not deserialize config data: %s' % e)

    if not isinstance(conf, dict):
        raise ConfigurationError('Deserialized config must be a dict, got "%s"'
                                 % conf)
    return conf

def get_settings_for_bundle(settings, path, default=None):
    """
    Extracts and returns settings for given bundle from given configuration
    dictionary.

    Raises `KeyError` if the settings dictionary does not specify anything for
    this bundle or the `bundles` section at all. Empty (but existing) bundle
    settings do not raise the exception.

    :param settings:
        a settings dictionary, must have the key "bundles" with a
        sub-dictionary with bundle module path as keys. There are no
        constraints on values. It is OK to pass `None`.
    :param path:
        the *full* path to the module that represents a bundle (e.g.
        `tool.ext.jinja`).

    Example settings (in YAML)::

        bundles:
            tool.ext.templating:
                searchpaths: ['templates/']
            tool.ext.documents: null    # --> `None` in Python

    .. note::

        The returned value is a deep copy of the original value. This allows
        the client code to modify the value (e.g. use `conf.pop('foo')`)
        without breaking the orginal configuration.

    """
    try:
        bundles = settings['bundles']
    except KeyError:
        raise KeyError('There is no section "bundles" in the settings.')
    if path in bundles:
        return deepcopy(bundles[path])
    if default is not None:
        return default
    raise KeyError('Bundle "{path}" is not in settings'.format(**locals()))


def merge_dicts(old, new):
    def both_dicts(a, b):
        return isinstance(a, dict) and isinstance(b, dict)
    assert both_dicts(old, new)
    combined = old.copy()
    stack = [(combined, new)]
    while stack:
        cmb, upd = stack.pop()
        for key in upd:
            if key in cmb and both_dicts(cmb[key], upd[key]):
                stack.append((cmb[key], upd[key]))
            else:
                cmb[key] = upd[key]
    return combined
