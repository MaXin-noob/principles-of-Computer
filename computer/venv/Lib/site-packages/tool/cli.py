# -*- coding: utf-8 -*-
"""
Command-line interface
======================

Shell commands subsystem for :term:`CLI`. A thin wrapper around Argh_ which is
in turn a thin wrapper around `argparse` (bundled with Python 2.7+ and
available as a separate package).

The module also initializes these tools for advanced terminal text output:

colorama_
    Cross-platform. Exports three of its objects: :class:`Fore`, :class:`Back`
    and :class:`Style`. If the module is not available, dummy no-op objects are
    exported instead.
blessings_
    More powerful than `colorama` but doesn't provide native support for
    Windows. Exports `term` object which is a :class:`blessings.Terminal`
    instance. If the module is not available, `term` becomes ``None``.

.. _Argh: http://pypi.python.org/pypi/argh
.. _colorama: http://pypi.python.org/pypi/colorama
.. _blessings: http://pypi.python.org/pypi/blessings

Overview
--------

Basic usage::

    from tool.cli import ArghParser, arg

    @arg('word')
    def echo(args):
        print 'You said {0}'.format(args.word)

    if __name__=='__main__':
        parser = ArghParser()
        parser.add_commands([echo])
        parser.dispatch()

Usage with application manager::

    from tool import ApplicationManager
    from tool.cli import ArghParser, arg

    @arg('word')
    def echo(args):
        print 'You said {0}'.format(args.word)

    app = ApplicationManager('conf.yaml')

    if __name__=='__main__':
        app.add_commands([echo])
        app.dispatch()

You can call :meth:`tool.application.ApplicationManager.dispatch` instead of
:func:`dispatch`, they are exactly the same.

To register a command just wrap it in the :func:`command` decorator and import
the module that contains the command before dispatching.

API reference
-------------
"""

__all__ = [
    # argument parsing:
    'ArghParser', 'alias', 'arg', 'command', 'confirm', 'CommandError',
    'plain_signature', 'wrap_errors',
    # terminal colors:
    'Fore', 'Back', 'Style',
]

from argh import (
    ArghParser, alias, arg, command, confirm, CommandError, plain_signature,
    wrap_errors,
)

try:
    from colorama import init, Fore, Back, Style
except ImportError:
    class Dummy(object):
        def __getattr__(self, name):
            return ''
    Fore = Back = Style = Dummy()
    init = lambda x=None:None

try:
    from blessings import Terminal
except ImportError:
    term = None
else:
    term = Terminal()
