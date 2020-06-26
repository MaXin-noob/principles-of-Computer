# -*- coding: utf-8 -*-
"""
HTTP Serving
============

:state: stable
:dependencies: Werkzeug_
:feature: `http`

This extension handles everything related to serving a web application. It does
not however include the application itself (middleware, routing, etc.).

.. _Werkzeug: http://werkzeug.pocoo.org

API reference
-------------
"""
from werkzeug import run_simple, cached_property
from tool.plugins import BasePlugin
from tool.cli import arg
from tool import app


__all__ = ['Server']


def make_serve(application):
    """Factory that expects an :class:`ApplicationManager` instance and returns
    the CLI command `serve` bound to that instance.

    We could do without the factory and simply peek into thread-local variable
    `tool.app` but when threading is activated `by` the command (e.g. with
    autoreloader), that variable gets lost. So we explicitly inform this very
    command about the application.
    """
    @arg('--host', default='localhost')
    @arg('-p', '--port', default=6060,
         help='do not reload the server on code change')
    @arg('--noreload', default=False, action='store_true')
    @arg('--nodebug', default=False, action='store_true',
         help='do not use the interactive debugger')
    def serve(args):
        """ Runs development server for your application. Wrapper for Werkzeug's
        run_simple_ function.

        Note that without ``nodebug`` this will wrap the application into
        `werkzeug.debug.DebuggedApplication` without touching the application's
        WSGI stack, i.e. this middleware will *not* be visible in the output of
        :func:`tool.debug.print_wsgi_stack`. The reason is simple: this command
        only serves the application but does not configure it; therefore it should
        not modify the internals of the object being served.

        .. _run_simple: http://werkzeug.pocoo.org/documentation/dev/serving.html#werkzeug.run_simple
        """
        run_simple(
            application = application,
            hostname = args.host,
            port = args.port,
            use_reloader = not args.noreload,
            use_debugger = not args.nodebug,
        )
    return serve


class Server(BasePlugin):
    """
    :Configuration: none
    :Requires: none
    :Provides:
        commands:
          * `http serve` — runs a development server for your application
    """
    features = 'http'
    commands = cached_property(lambda self: [make_serve(self.app)])
