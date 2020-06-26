# -*- coding: utf-8 -*-

"""
Built-in commands
=================

Tool provides a set of built-in commands for :doc:`cli`.
"""

from werkzeug import run_simple
#from werkzeug.script import make_shell

from tool.cli import arg
from tool import app


__all__ = ['make_serve', 'shell']


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

@arg('--plain', default=False)
def shell(args):
    """ Spawns an interactive Python shell for your application. Picks the
    first choice of: bpython, IPython, plain Python. Use --plain to force plain
    Python shell.
    """
    # TODO: this should not trigger the WSGI/routing stuff to load.
    # maybe load web-related things and extensions when needed only?
    # See e.g. http://dev.pocoo.org/projects/werkzeug/browser/examples/manage-simplewiki.py
    init_func = lambda: {'app': app}
    sh = make_shell(init_func, plain=args.plain)
    sh()

def make_shell(init_func=None, banner=None, plain=False):
    """Returns an action callback that spawns a new interactive
    python shell.

    :param init_func: an optional initialization function that is
                      called before the shell is started.  The return
                      value of this function is the initial namespace.
    :param banner: the banner that is displayed before the shell.  If
                   not specified a generic banner is used instead.
    :param plain: if set to `True`, default Python shell is used. If set to
                  `False`, bpython or IPython will be used if available (this
                  is the default behaviour).

    This function is identical to that of Werkzeug but allows using bpython.
    """
    banner = banner or 'Interactive Tool Shell'
    init_func = init_func or dict
    def pick_shell(banner, namespace):
        """
        Picks and spawns an interactive shell choosing the first available option
        from: bpython, IPython and the default one.
        """
        if not plain:
            # bpython
            try:
                import bpython
            except ImportError:
                pass
            else:
                bpython.embed(namespace, banner=banner)
                return

            # IPython
            try:
                import IPython
            except ImportError:
                pass
            else:
                sh = IPython.Shell.IPShellEmbed(banner=banner)
                sh(global_ns={}, local_ns=namespace)
                return

        # plain
        from code import interact
        interact(banner, local=namespace)
        return

    return lambda: pick_shell(banner, init_func())
