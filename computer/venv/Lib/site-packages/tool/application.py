# -*- coding: utf-8 -*-
#
#  Copyright (c) 2009—2011 Andrey Mikhailenko and contributors
#
#  This file is part of Tool.
#
#  Tool is free software under terms of the GNU Lesser General Public License
#  version 3 (LGPLv3) as published by the Free Software Foundation. See the
#  file README for copying conditions.
#
"""
Application
===========

This is the core of Tool. You can safely ignore it and use other parts of the
package, but in most cases you will really need the power of
:class:`ApplicationManager`. It's also a good idea to subscribe to signals that
it emits.

API reference
-------------
"""
import os
from tool.log import logging, setup_logging

logger = logging.getLogger('tool.application')

from werkzeug import Response, Request, responder, cached_property
from werkzeug.routing import Map, Rule, Submount
from werkzeug.script import make_shell

from tool import cli, conf, signals
from tool.context_locals import local
from tool.importing import import_module, import_attribute
import commands



__all__ = [
    'Application', 'WebApplication', 'request_ready',
    #'wsgi_app_ready', 'app_manager_ready',
]


# signals
request_ready     = signals.Signal('request_ready')
#urls_bound        = signals.Signal('urls_bound')
#wsgi_app_ready    = signals.Signal('wsgi_app_ready')
#app_manager_ready = signals.Signal('app_manager_ready')
#pre_app_manager_ready = signals.Signal('pre_app_manager_ready')


class ConfigurationError(Exception):
    "Raised by application configurator if something's wrong."
    pass


class Application(object):
    """
    A CLI application.

    :param settings:

        dictionary or path to a YAML file from which the dictionary can be
        obtained. If `None`, path to the YAML file is assumed to be in the
        environment variable ``TOOL_CONF``. If it is empty too, empty
        configuration is taken.

    :param extra_settings:

        merged into `settings`; nested dictionaries are updated instead of
        being replaced as it would happen with ``dict.update()``.

    Usage::

        #!/usr/bin/env python

        from tool import Application

        app = Application('conf.yaml', 'local.yaml')

        if __name__=='__main__':
            app.dispatch()    # process sys.argv and call a command

    The code above is a complete management script. Assuming that it's saved as
    `app.py`, you can call it this way::

        $ ./app.py shell python
        $ ./app.py http serve
        $ ./app.py import-some-data

    All these commands are exported by certain extensions and handled by
    :meth:`~Application.dispatch`. See :doc:`cli` for details.

    """

    #-----------------+
    #  Magic methods  |
    #-----------------+

    def __init__(self, settings=None, extra_settings=None):   #, url_map=None):
        self.cli_parser = cli.ArghParser()
        self.settings = self._prepare_settings(settings, extra_settings)
        self._register()
        self._setup_logging()
        self._load_extensions()

    #-------------------+
    #  Private methods  |
    #-------------------+

    def _register(self):
        """
        Makes the app available from any part of app, incl. from shell.

        After this method is called, `context.app_manager` is set to current
        ApplicationManager instance. If you later wrap it in WSGI middleware
        without using :meth:`~ApplicationManager.wrap_in`, the registered
        instance will *not* change (see `wrap_in` documentation).
        """
        logger.debug('Registering the application in the context '
                     '{0}...'.format(local))
        local.app_manager = self

    def _prepare_settings(self, settings, extra):
        logger.debug('Preparing settings...')
        basic_dict = self._prepare_settings_dict(settings)
        extra_dict = self._prepare_settings_dict(extra)
        return conf.merge_dicts(basic_dict, extra_dict)

    def _prepare_settings_dict(self, value):
        if value is None:
            value = os.environ.get('TOOL_CONF', None)
            if not value:
                return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, basestring):
            return conf.load(value)
        raise TypeError('expected None, dict or string, got %s' % value)

    def _setup_logging(self):
        conf = self.settings.get('logging')
        setup_logging(conf)

    def _load_extensions(self):
        # configured extensions (instances) are indexed by full dotted path
        # (including class name). It is also possible to access them by feature
        # name: see Application.get_feature().

        logger.debug('Loading extensions...')

        _extensions = {}
        _features = {}

        # collect extensions, make sure they can be imported and group them by
        # identity. The identity is declared by the extension class. It is usually
        # the dotted path to the extension module but can be otherwse if the
        # extension implements a named role (e.g. "storage" or "templating").
        if not 'extensions' in self.settings:
            import warnings
            warnings.warn('No extensions configured. Application is unusable.')

        for path in self.settings.get('extensions', []):
            assert isinstance(path, basestring), (
                'cannot load extension by module path: expected a string, '
                'got {0}'.format(repr(bundle)))
            logger.debug('Loading (importing) extension {0}'.format(path))
            #
            # NOTE: the "smart" stuff is commented out because in most cases
            # this hides the valuable call stack; moreover, this happens on
            # start so wrapping is really unnecessary.
            #
            #try:
            #    cls = import_attribute(path)
            #except (ImportError, AttributeError) as e:
            #    raise ConfigurationError(
            #        'Could not load extension "{0}": {1}'.format(path, e))
            #
            cls = import_attribute(path)
            conf = self.settings['extensions'][path]

            _extensions[path] = cls, conf
            if getattr(cls, 'features', None):
                # XXX here "features" is a verb, not a noun; may be misleading
#                for feature in cls.features:
                if not isinstance(cls.features, basestring):
                    raise ConfigurationError(
                        'Extension should supply its feature name as string; '
                        '{path} defines {cls.features}'.format(**locals()))
                assert cls.features not in _features, (
                    '{feature} must be unique'.format(**locals()))
                _features[cls.features] = path

        # now actually initialize the extensions and save them to the application
        # manager instance. This involves checking dependencies. They are
        # listed as dotted paths ("foo.bar") or features ("{quux}"). The
        # features must be dereferenced to dotted paths. We can only do it
        # after we have an imported class that declares itself an
        # implementation of given feature (i.e. "class MyExt: features='foo'").
        # That's why we are messing with two loading stages.

        self._extensions = {}
        self._features = _features

        stacked = {}
        loaded = {}

        # TODO: refactor (too complex, must be easily readable)
        def load_extension(path):
            if path in stacked:
                # raise a helpful exception to track down a circular dependency
                classes = [_extensions[x][0] for x in stacked]
                related = [p for p in classes
                              if p.requires and path in [r.format(**_features) for r in p.requires]]
                strings = ['.'.join([p.__module__,p.__name__])
                                 for p in related]
                raise RuntimeError('Cannot load extension "{0}": circular '
                                   'dependency with {1}'.format(path,
                                                                strings))

            if path in loaded:
                # this happens if the plugin has already been loaded as a
                # dependency of another plugin
                logger.debug('Already loaded: {0}'.format(path))
                return

            cls, conf = _extensions[path]

            assert path not in self._extensions, (
                'Cannot load extension {0}: path "{1}" is already loaded as '
                '{2}.'.format(cls, path, self._extensions[path]))

            stacked[path] = True  # to prevent circular dependencies

            # load dependencies
            if getattr(cls, 'requires', None):
                assert isinstance(cls.requires, (tuple, list)), (
                    '{0}.{1}.requires must be a list or tuple'.format(
                        cls.__module__, cls.__name__))
                for req_string in cls.requires:
                    # TODO: document this behaviour, i.e. "{templating}" -> "tool.ext.jinja"
                    try:
                        requirement = req_string.format(**_features)
                    except KeyError as e:
                        raise ConfigurationError(
                            'Unknown feature "{0}". Expected one of '
                            '{1}'.format(e, list(_features)))

                    logger.debug('Dependency: {0} requires {1}'.format(path, requirement))
                    if path == requirement:
                        raise ConfigurationError('{0} requires itself.'.format(path))
                    if requirement not in _extensions:
                        raise ConfigurationError(
                            'Plugin {0}.{1} requires extension "{2}" which is '
                            'not configured. These are configured: '
                            '{3}.'.format(cls.__module__, cls.__name__,
                                          requirement, _extensions.keys()))
                    load_extension(requirement)  # recursion

            # initialize and register the extension
            extension = cls(self, conf)
            self._extensions[path] = extension

            loaded[path] = True
            stacked.pop(path)

        # load each extension with recursive dependencies
        for path in _extensions:
            load_extension(path)

    #----------------------+
    #  Public API methods  |
    #----------------------+

    def dispatch(self):
        """Dispatches commands (CLI).
        """
        self._register()

        # XXX using undocumented hook to work around the colorama
        # initialization stuff contaminating the autocompletion choices
        def pre_call(args):
            cli.init()
        self.cli_parser.dispatch(pre_call=pre_call)

    def get_extension(self, name):
        """Returns a configured extension object with given dotted path."""
        try:
            return self._extensions[name]
        except KeyError:
            raise RuntimeError('Unknown extension "{0}". Expected one of '
                               '{1}'.format(name, list(self._extensions)))

    def get_feature(self, name):
        """Returns a configured extension object for given feature.
        """
        try:
            path = self._features[name]
        except KeyError:
            raise RuntimeError('Unknown feature "{0}". Expected one of '
                               '{1}'.format(name, list(self._features)))
        try:
            return self._extensions[path]
        except KeyError:
            raise RuntimeError('Feature "{name}" is registered for class '
                               '"{path}" which instance is '
                               'missing.'.format(**locals()))


class WebApplication(Application):
    """A WSGI-enabled :class:`Application`. Supports common WSGI middleware.
    Can be configured to run a shell script including a WSGI application
    server; can *be* run as a WSGI application itself (i.e. is callable).

    Please note that this class does not provide URL routing, web server,
    templating and other features common for web applications; you need to
    configure relevant extensions that provide these features. See :doc:`ext`
    for a list of extensions bundled with `Tool`.
    """
    #-----------------+
    #  Magic methods  |
    #-----------------+

    def __init__(self, *args, **kwargs):
        self.wsgi_stack = []
        super(WebApplication, self).__init__(*args, **kwargs)

    def __call__(self, environ, start_response):
        logger.debug('Calling WSGI application')
        self._register()  # XXX looks like this is needed e.g. with reloader
        return self.wsgi_app(environ, start_response)

    #-------------------+
    #  Private methods  |
    #-------------------+

    def _innermost_wsgi_app(self):
        """
        Creates and returns the innermost WSGI application. Cached.
        """
        def application(environ, start_response):
            response = Response('WSGI application without routing', status=500)
            return response(environ, start_response)
        return application

    #----------------------+
    #  Public API methods  |
    #----------------------+

    @cached_property
    def wsgi_app(self):
        """
        Processes the stack of WSGI applications, wrapping them one in
        another and executing the result::

            app = tool.Application()
            app.wrap_in(SharedDataMiddleware, {'/media': 'media'})
            app.wrap_in(DebuggedApplication, evalex=True)
            >>> app.wsgi_app
            <DebuggedApplication>

        See, what we get is the last application in the list -- or the
        *outermost middleware*. This is the real WSGI application.

        Result is cached.
        """
        logger.debug('Compiling WSGI application')
        outermost = self._innermost_wsgi_app
        for factory, args, kwargs in self.wsgi_stack:
            _tmp_get_name=lambda x: getattr(x, '__name__', type(x).__name__)
            logger.debug('Wrapping WSGI application in {0}'.format(
                                _tmp_get_name(factory)))
            logger.debug('    with args: {0}'.format(args))
            logger.debug('    with kwargs: {0}'.format(kwargs))
            #print 'wrapping', _tmp_get_name(outermost), 'in', _tmp_get_name(factory)
            outermost = factory(outermost, *args, **kwargs)

        # activate debugger
        if self.settings.get('debug', False):
            logger.debug('Wrapping WSGI application in debugger middleware')
            from werkzeug import DebuggedApplication
            outermost = DebuggedApplication(outermost, evalex=True)

        #wsgi_app_ready.send(sender=self, wsgi_app=outermost)

        return outermost

    def wrap_in(self, func, *args, **kwargs):
        """
        Wraps current application in given WSGI middleware. Actually just
        appends that middleware to the stack so that is can be called later on.

        Usage::

            app.wrap_in(SharedDataMiddleware, {'/media': 'media'})
            app.wrap_in(DebuggedApplication, evalex=True)

        ...which is identical to this::

            app.wsgi_stack.append([SharedDataMiddleware,
                                   [{'/media': 'media'], {}])
            app.wsgi_stack.append([DebuggedApplication, [], {'evalex': True}])

        In rare cases you will need playing directly with the stack; in most
        cases wrapping is sufficient as long as the order is controlled by you.

        It is possible to wrap the WSGI application provided by the
        ApplicationManager into WSGI middleware without using
        :meth:`~WebApplication.wrap_in`. However, the resulting WSGI
        application will not have the Tool API and will only conform to the
        WSGI API so you won't be able to use the :class:`WebApplication`
        methods::

            from tool import WebApplication
            from werkzeug import DebuggedApplication

            app = WebApplication('conf.yaml')
            app = DebuggedApplication(app)   # WRONG!

            if __name__=='__main__':
                app.dispatch()   # will NOT work: API is wrapped

        Still, this doesn't matter if you are not going to use the
        :class:`Application` API after wrapping it in middleware.

        Another option::

            app.wsgi_app = DebuggedApplication(app.wsgi_app)

        This is much better as it doesn't hide away the API. However, it does
        break middleware introspection (see :doc:`debug`) so use with care.

        In any case, the safest method is :meth:`WebApplication.wrap_in`.
        """
        self.wsgi_stack.append((func, args, kwargs))


def ApplicationManager(*args, **kwargs):
    import warnings
    warnings.warn('ApplicationManager is deprecated, use '
                  'Application or WebApplication instead.',
                  DeprecationWarning)
    return WebApplication(*args, **kwargs)
