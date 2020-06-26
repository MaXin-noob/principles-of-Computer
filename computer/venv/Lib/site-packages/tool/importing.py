# -*- coding: utf-8 -*-

import sys


def import_module(path):
    __import__(path, globals(), locals(), [], -1)
    return sys.modules[path]

def import_attribute(path):
    if not '.' in path:
        raise AttributeError('Could not import "%s" as attribute: expected '
                             'dot-delimited path but there are no dots in it.'
                             % path)
    module_path, attr_name = path.rsplit('.', 1)
    module = __import__(module_path, globals(), locals(), [attr_name], -1)
    return getattr(module, attr_name)

def import_whatever(path):
    try:
        return import_attribute(path)
    except AttributeError:
        try:
            return import_module(path)
        except ImportError as e:
            raise ImportError('Could not import "%s" neither as module nor as '
                              'attribute: %s' % (path, e))
