# -*- coding: utf-8 -*-
"""
Plugins
=======

Tool provides a simple API for plugins. In fact, even the basic functionality
(such as standard commands, templating and so on) is extracted to plugins. This
makes Tool extremely flexible. You can swap and drop in almost any component.

Moreover, Tool provides a very simple way to ensure that all plugins are loaded
in correct order and all dependencies are configured. This makes plugins indeed
"pluggable" as opposed to the Django applications.

.. warning::

    This document is a draft; for now see :doc:`ext` (outdated)

A Tool extension is a class (or a factory) that conforms to a minimal API. It
is initialized with two arguments: the :class:`~tool.application.Application`
instance and the extension configuration dictionary. It can whatever it needs
to do then. The normal workflow is implemented in :class:`BasePlugin`. You can
subclass it and override any attribute you need to tune the behaviour and
specify the contribution of the extension to the application.

Interaction between extensions
------------------------------

Extensions can interact with each other. It is strongly adviced that they only
access each other's instances through
:meth:`tool.application.Application.get_extension` or
:meth:`tool.application.Application.get_feature` and only use the extensions'
explicitly published and documented API instead of internal states.

For example, if we have this extension::

    class Foo(BasePlugin):
        def make_env(self, bar=123):
            return {'bar': bar + 1}

        def get_bar(self):
            return self.env['bar']

...then another extension, which is dependent on it, should access the `bar`
variable this way::

    class Quux(BasePlugin):
        requires = ['foo_ext.Foo']
        def make_env(self):
            foo = self.app.get_extension('foo_ext.Foo')
            foobar = foo.get_bar()
            return {'foobar': foobar}

Of course this is also possible::

    foo = app.get_extension('foo_ext.Foo')
    foobar = foo.env['bar']

...but extension environment is *not* public API. It may change and these
changes will break all dependent extensions. So the extensions should properly
expose special methods and gradually remove them (by deprecating) if they are
no more in use.

Features
--------

TODO

Best practices
--------------

To keep the extensions truly reusable, it is a good idea to follow these
principles:

* Simple is better than complex
* Explicit is better than implicit
* Separation of concerns

And probably the most important thing to keep in mind: **You never know how the
application will be configured**.

Here are some more concrete suggestions:

* *Separate interfaces.* If your extension provides both commands and views
  (i.e. supports both command-line interface and WSGI via routing), separate
  these interfaces. Expose two extension classes: a CLI-only version and an
  extended version that supports routing. This allows configuring truly
  CLI-only applications for which fast cold start is crucial. Using purely CLI
  extension classes ensures that no routing- or templating-related stuff is
  loaded.
* *Don't import.* Try not to import anything directly from other extensions.
  Use their class API instead. Remember that all dependencies will be reliably
  configured before `make_env` is called. Write your own extensions so that
  importing your extension module will not trigger an extra imports. For
  example, this is not CLI-safe::

    # this imports the templating stuff even if you only need FooCLI
    from tool.ext.templating import register_templates

    class FooCLI(BasePlugin):
        commands = ...

    class FooWeb(FooCLI):
        requires = ['templating']
        def make_env(self):
            register_templates(__name__)

  This version is safe because the importing depends on the configuration::

    class FooCLI(BasePlugin):
        commands = ...

    class FooWeb(FooCLI):
        requires = ['templating']
        def make_env(self):
            templating = self.app.plugins['templating']
            templating.register_templates(__name__)

API reference
-------------
"""
import logging
logger = logging.getLogger(__name__)

from tool import app


__all__ = ['BasePlugin', 'get_feature', 'features', 'requires']


def features(feature):
    """
    Adds attribute `features` to the setup function. Usage::

        @features('database')
        def setup(app, conf):
            conn = sqlite3.connect(conf.get('uri'))
            return {'db': conn}

    """
    def wrapper(func):
        func.features = feature
        return func
    return wrapper

def requires(*specs):
    """
    Adds attribute `requires` to the setup function. Usage::

        @requires('{database}', '{templating}', 'foo.bar.web_setup')
        def setup(app, conf):
            assert not conf
            return {}

    """
    def wrapper(func):
        func.requires = specs
        return func
    return wrapper


# TODO: rename to BaseExtension
class BasePlugin(object):
    """ Abstract plugin class. Represents a plugin with configuration logic.
    Must be not be used directly. Concrete module should either subclass the
    `BasePlugin` verbosely or use the :func:`make_plugin` factory. Usage::

        class MyPlugin(BasePlugin):
            pass

    That's enough for a plugin that requires some initialization logic but does
    not support external configuration. If you need to pass some settings to
    the plugin, do this::

        class SQLitePlugin(BasePlugin):
            def make_env(self, db_path='test.sqlite'):
                conn = sqlite3.connect(db_path)
                return {'connection': conn}

    Here's how the configuration (in YAML) for this plugin could look like
    (given that the class is located in the module "sqlite_plugin")::

        plugins:
            sqlite_plugin.SQLitePlugin:
                db_path: "databases/orders.db"

    And if you don't need to change the defaults or the plugin doesn't expect
    any configuration at all, just do this::

        plugins:
            sqlite_plugin.SQLitePlugin: null

    This tells the application to load and configure the plugin with default
    settings.
    """
#   identity = None    # see method identify()
    requires = None
    commands = None
    features = None
#   provides

    def __init__(self, app, conf):
        logger.debug('Configuring {0} as {1}...'.format(self,
                                                          self.features))


        if hasattr(self, 'identity'):
            import warnings
            warnings.warn('{0}.identity is deprecated. Use "features" '
                          'instead.'.format(self), DeprecationWarning)

        self.app = app
        self.env = self.make_env(**conf or {})
        self.contribute_to_app(app)

    def __str__(self):
        return '{0}.{1}'.format(self.__module__, self.__class__.__name__)

    def __repr__(self):
        return '<{0}>'.format(str(self))

    def make_env(self, **settings):
        """ Processes the plugin-related configuration and returns a dictionary
        representing the plugin state. For example, if the plugin configuration
        specified database connection settings, then the returned dictionary
        would contain the actual connection to the database.
        """
        if settings:
            raise KeyError('Module {0} does not accept any configuration '
                           'options.'.format(self))
        return {}

    def contribute_to_app(self, app):
        # collect commands from the plugin
        if self.commands:
            # FIXME feature? nope, it's plural. What about routing? Say,
            # mounting commands within a config branch?

            namespace = (self.features or self.__class__.__module__)
            #namespace = path.rpartition('.')[0]
            namespace = namespace.replace('_','-').replace('.','-')
            logger.debug('adding {0} in {1}'.format(self.commands, self))
            app.cli_parser.add_commands(self.commands,
                                        namespace=namespace,
                                        title=self.__doc__,
                                        description=self.__doc__)

        # collect middleware from the plugin
        middlewares = self.get_middleware() or []
        for middleware in middlewares:
            mw_class, mw_args, mw_kwargs = middleware
            app.wrap_in(mw_class, *mw_args, **mw_kwargs)

    def get_middleware(self):
        """ Returns either `None` or a tuple of middleware class and the
        settings dictionary. Called by the application manager after the
        plugin environment is initialized. A simplified real-life example::

            class RepozeWhoPlugin(BasePlugin):

                def make_env(self, **settings):
                    return {'middleware_config': settings['config']}

                def get_middleware(self):
                    AuthenticationMiddleware, self.env['middleware_config']

        """
        return None

'''
def make_plugin(module_path):
    """ Plugin class factory, semantically close to ``Flask(__name__)``.
    Usage::

        MyPlugin = make_plugin(__name__)

    If the above code appears in module `foo.bar`, then the plugin instance
    will be available in the application manager at the same path, and the
    settings will be expected to be defined as follows (a YAML example)::

        plugins:
            foo.bar.MyPlugin: null

    """
    name_lowercase = module_path.split('.')[-1]
    name = ''.join(x.capitalize() for x in name_lowercase.split('_'))
    return type(name, (ToolModule,), {'identifier': module_path})
'''

def get_feature(name):
    """ Returns the extension class instance """
    try:
        return app.get_feature(name)
    except KeyError:
        raise KeyError('Plugin with identity "{0}" does not exist. Configured '
                       'plugins are: {1}'.format(identity, app._features.keys()))
