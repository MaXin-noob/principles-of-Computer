from tool import app
from tool.cli import alias, arg
from tool.plugins import features


FEATURE = 'shell'



#class Shell(BasePlugin):
#    features = 'shell'
#    commands = [python]    # TODO make it "shell" instead of "shell python"



@features(FEATURE)
def setup_shell(app, conf):
    app.cli_parser.add_commands([python_shell])

def Shell(app, conf):
    import warnings
    warnings.warn('Shell class is deprecated, use function setup_shell() '
                  'instead', DeprecationWarning)
    return setup_shell(app, conf)


@alias(FEATURE)
@arg('--plain', default=False)
def python_shell(args):
    """ Spawns an interactive Python shell for your application. Picks the
    first choice of: bpython, IPython, plain Python. Use --plain to force plain
    Python shell.
    """
    # TODO: this should not trigger the WSGI/routing stuff to load.
    # maybe load web-related things and extensions when needed only?
    # See e.g. http://dev.pocoo.org/projects/werkzeug/browser/examples/manage-simplewiki.py
    def init_func():
        ns = {'app': app}
        # FIXME this should be conditional
        db_ext = app.get_feature('document_storage')
        ns.update(db=db_ext.default_db)
        return ns
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
