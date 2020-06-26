# -*- coding: utf-8 -*-
"""
Template engine (Jinja2)
========================

:state: stable
:dependencies: `Jinja2`_ and/or `Mako`_
:feature: `templating`

.. _Jinja2: http://jinja.pocoo.org/2/
.. _Mako: http://makotemplates.org

This extension provides a uniform API for two popular templating engines:

* :class:`JinjaPlugin` for Jinja2_, and
* :class:`MakoPlugin` for Mako_.

You should configure one of them.

Configuration
-------------

Typical configuration example (YAML)::

    tool.ext.templating.JinjaPlugin: null

This configuration preserves the default values. See section "Overriding
templates" below for more information on configuration options.

Of course you can replace :class:`JinjaPlugin` with :class:`MakoPlugin`.

Usage
-----

Simple example (assuming that the code is in `my_extension/__init__.py`)::

    from tool import app
    from tool.plugins import BasePlugin

    class Foo(BasePlugin):
        def make_env(self):
            t = app.get_feature('templating')
            t.register_templates(__name__)

In this case the absolute path to templates will be constructed from module
location and the default name for template directory, i.e. something like
`/path/to/my_extension/templates/`.

The templates will be available as ``my_extension/template_name.html``.

Advanced usage::

    t.register_templates('proj.extension_foo', 'data/tmpl/', prefix='proj')

In this case the absolute path to templates will be something like
`/path/to/proj/extension_foo/data/tmpl/`.

The templates will be available as ``proj/template_name.html``.

Bundle templates
----------------

`Jinja2`_ provides excellent means to configure the way templates are located
and loaded. Tool looks up the template in this order:

* the project-level search paths (first full match wins);
* the registered prefixes (i.e. the path starts with a known extension name).

The `prefixes` can be registered with :func:`register_templates`. For example,
we have created an extension with this layout::

    my_extension/
        templates/
            foo.html
        __init__.py


To register the extension's templates, add this to its `__init__.py`::

    from tool.ext.templating import register_templates

    register_templates(__name__)

This will make our `foo.html` globally available as `my_extension/foo.html`.

There are other ways to register the templates. Please consult the code to find
them out. Anyway, templates *must* be registered explicitly. Tool lets you
organize the extensions the way you want and therefore expects that you tell what
is where.

Overriding templates
--------------------

Web-oriented Tool extensions usually provide templates. Sometimes you'll want to
replace certain templates. Let's say we are not comfortable with a default
:doc:`Admin <ext_admin>` template and want to override it. Let's create a
project-level directory for templates and put our customized templates there::

    some_site/
        templates/
            admin/
                object_list.html
        conf.yaml
        manage.py

As you see, the template path within `templates/` will be
`admin/object_list.html` (`admin` is the natural template prefix for
`tool.ext.admin`, see :func:`register_templates` for details).

Now let's edit out `conf.yaml` and let the application know about the
`templates/` directory::

    extensions:
        tool.ext.templating.JinjaPlugin:
            searchpaths: ['templates']

Well, actually this is the default setting. If `searchpaths` is not defined at
all, it is assumed to be ``['templates']``.

Now the template `admin/object_list.html` will be picked from the `templates/`
directory. All other admin templates remain defaults.

This way you can override any bundle's template.

API reference
-------------

Both :class:`JinjaPlugin` and :class:`MakoPlugin` provide two important
methods: `register_templates` to declare the template directories, and
`render_template` to actually use them.

"""
from copy import deepcopy
from functools import wraps
import logging
from werkzeug import Response
from tool import app
from tool.routing import url_for
from tool.signals import called_on, Signal
from tool.application import request_ready
from tool.plugins import get_feature
import tool.plugins

logger = logging.getLogger(__name__)

try:
    import jinja2 #import Environment, ChoiceLoader, FileSystemLoader, PackageLoader, PrefixLoader
except ImportError:
    jinja2 = None

try:
    import mako
    import mako.lookup
except ImportError:
    mako = None


__all__ = ['JinjaPlugin', 'MakoPlugin', 'as_html', 'register_templates',
           'render_template', 'render_response']


FEATURE = 'templating'
DEFAULT_PATH = 'templates'
DEFAULT_TEMPLATE_FUNCTIONS = {
    'url_for': url_for,
}


class BaseTemplatingPlugin(tool.plugins.BasePlugin):

    features = FEATURE

    def register_templates(self, module_path, dir_name=DEFAULT_PATH,
                           prefix=None):
        """
        Registers given extension's templates in the template loader.

        :param module_path:
            The dotted path to the bundle module. The absolute path to the
            templates will depend on the module location.
        :param dir_name:
            Templates directory name within given module. Default is
            ``templates``. Relative to module's ``__file__``.
        :param prefix:
            The prefix for templates. By default the rightmost part of the
            module name is used e.g. ``tool.ext.admin`` will have the prefix
            ``admin``.

        """
        raise NotImplementedError

    def update_template_context(self, data):
        raise NotImplementedError

    def render_template(self, path, context):
        """Renders given template file with given context and returns the
        result.

        :param path:
            Path to the template file. Should be previously registered with
            :meth:`register_templates` and/or belong to the directories listed
            is `searchpaths` (see configuration).
        :param context:
            A dictionary.

        """
        template = self.env['templating_env'].get_template(path)
        return template.render(context)


class JinjaPlugin(BaseTemplatingPlugin):
    """Offers integration with Jinja2_."""
    def make_env(self, **settings):
        if not jinja2:
            raise ImportError('Could not import package jinja2.')

        paths = settings.pop('searchpaths', [DEFAULT_PATH])

        loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(paths),
            jinja2.PrefixLoader({})
        ])

        jinja_env = jinja2.Environment(loader=loader, **settings)
        jinja_env.globals.update(DEFAULT_TEMPLATE_FUNCTIONS)

        return {
            'templating_env': jinja_env,
        }

    def register_templates(self, module_path, dir_name=DEFAULT_PATH,
                           prefix=None):
        "See :func:`register_templates`."
        _prefix = module_path.split('.')[-1] if prefix is None else prefix

        jinja_env = self.env['templating_env']
        loaders = jinja_env.loader.loaders
        assert len(loaders) == 2
        assert isinstance(loaders[1], jinja2.PrefixLoader)
        loader = jinja2.PackageLoader(module_path, dir_name)
        loaders[1].mapping[_prefix] = loader
    register_templates.__doc__ = (
        BaseTemplatingPlugin.register_templates.__doc__)

    def update_template_context(self, data):
        self.env['templating_env'].globals.update(**data)


class MakoPlugin(BaseTemplatingPlugin):
    """Offers integration with Mako_."""
    def make_env(self, **settings):
        if not mako:
            raise ImportError('Could not import package mako.')

        paths = settings.pop('searchpaths', [DEFAULT_PATH])

        from mako.lookup import TemplateLookup
        loader = TemplateLookup(paths, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])

        return {
            'templating_env': loader,
            'context': DEFAULT_TEMPLATE_FUNCTIONS.copy(),
        }

    def register_templates(self, module_path, dir_name=DEFAULT_PATH,
                           prefix=None):
        import os.path
        from tool.importing import import_module
        mod = import_module(module_path)
        root = mod.__path__[0]
        path = os.path.join(root, dir_name)
        self.env['templating_env'].directories.append(path)
    register_templates.__doc__ = (
        BaseTemplatingPlugin.register_templates.__doc__)

    def update_template_context(self, data):
        self.env['context'].update(data)

    def render_template(self, path, context):
        template = self.env['templating_env'].get_template(path)
        combined_context = dict(self.env['context'], **context)
        return template.render_unicode(**combined_context)
    render_template.__doc__ = BaseTemplatingPlugin.render_template.__doc__



''' XXX bad idea: mixin methods should simply replace base methods without any
    super(), but here we really need to call both base and mixed-in methods.
    So it's easier to just call `register_templates` in `make_env`. But the
    underlying machinery can be somehow replaced.

class TemplatePluginMixin(object):
    "TODO: a mixin that automatically registers templates for given plugin."

    template_path = DEFAULT_PATH

    def make_env(self, **kwargs):
        raise NotImplementedError('TODO')
        # TODO: call register_templates(self.__module__,
        #                               dir_name=self.template_path)
        # the problem is in merging the base and mixed-in code


# TODO: use a mixin for plugin class, e.g.:
# class BlogPlugin(BasePlugin, TemplateMixin):
#     template_path = 'custom/template/path'
'''

def register_templates(module_path, dir_name=DEFAULT_PATH, prefix=None):
    """See :meth:`JinjaPlugin.register_templates` and
    :meth:`MakoPlugin.register_templates`.
    """
    app.get_feature(FEATURE).register_templates(module_path, dir_name, prefix)

@called_on(request_ready)
def add_request_to_templating_env(*args, **kwargs):
    logger.debug('Updating templating environment for the fresh Request object...')

    plugin = get_feature(FEATURE)
    plugin.update_template_context({'request': kwargs['sender']})


# Template rendering

def render_template(template_path, **extra_context):
    """
    Renders given template file with given context.

    :template_path:
        path to the template; must belong to one of directories listed in
        `searchpaths` (see configuration).
    """
    plugin = app.get_feature(FEATURE)
    return plugin.render_template(template_path, extra_context)

def render_response(template_path, mimetype='text/html', **extra_context):
    """TODO

    Internally calls :func:`render_template`.
    """
    return Response(
        render_template(template_path, **extra_context),
        mimetype=mimetype,
    )

def as_html(template_path):
    """
    Decorator for views. If the view returns a dictionary, given template is
    rendered with that dictionary as the context. If the returned value is not
    a dictionary, it is passed further as is.

    Internally calls :func:`render_response`.
    """
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            result = f(*args, **kwargs)
            if isinstance(result, dict):
                return render_response(template_path, **result)
            return result
        return inner
    return wrapper

'''
#@called_on(app_manager_ready)
def setup(sender, **kwargs):
    """
    Setup the ApplicationManager to use Jinja2.
    """
    manager = sender #kwargs['sender']

    try:
        conf = manager.get_settings_for_bundle(__name__, {})
    except KeyError:
        return False

    conf = {} if conf is None else conf

    print 'conf is', repr(conf)

    #conf = manager.settings['bundles']['jinja']
    #conf = deepcopy(manager.settings.get('templates', {}))

    # TODO: per bundle?
    #conf = dict(conf).setdefault('paths', ['templates'])

    #tmpl_paths = conf.get('paths', [])    #getattr(context, 'template_paths', [])
    #tmpl_paths.append('templates')    # TODO: per bundle?
    #context.template_paths = tmpl_paths

    paths = conf.pop('searchpaths', [DEFAULT_PATH])
    #fs_loader = FileSystemLoader(paths)

    # TODO: think of the best way to use http://jinja.pocoo.org/2/documentation/api#jinja2.PrefixLoader
    # and related stuff (they can be nested).
    # Requirements:
    # * /mybundle/templates/foo.html   (no /mybundle/templates/mybundle/foo.html)
    # * /templates/mybundle/foo.html   (appman-level override)
    #p=PackageLoader('tool.ext.admin', 'templates')
    #c=ChoiceLoader([p])
    #pref=PrefixLoader({'admin': c})
    #pref.list_templates()

    """
ChoiceLoader(
    FileSystemLoader([path_one, path_two]),
    PrefixLoader(
        PackageLoader(), .., N
    )
)
    """

    loader = ChoiceLoader([
        FileSystemLoader(paths),
        PrefixLoader({})
    ])

    # (also, mb jinja provides a signal and listens to it; when a bundle wants
    # to register a template, it just emits the signal and jinja either
    # collects the info until it's ready or processes immediately)

    #loader = FileSystemLoader(paths)
    #loader = ChoiceLoader([FileSystemLoader(path) for path in paths])

    tmpl_env = Environment(loader=loader, **conf)
    context.app_manager.live_conf[__name__]['templating_env'] = tmpl_env

    templating_ready.send(tmpl_env)
'''


"""
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, TemplateNotFound

def create_template_environment(searchpaths, loaders, globals, filters,
                                tests, env_kw):
    if not env_kw:
        env_kw = {}
    base_loader = FileSystemLoader(searchpaths)
    env_kw['loader'] = ChoiceLoader([base_loader] + loaders)
    if 'extensions' not in env_kw:
        env_kw['extensions']=['jinja2.ext.i18n', 'jinja2.ext.do',
                              'jinja2.ext.loopcontrols']

    loader = FileSystemLoader(paths)
    extensions = ['jinja2.ext.
    env = Environment(loader=loader, extensions=extensions)
    env.globals.update(globals)
    env.filters.update(filters)
    env.tests.update(tests)
    return env
"""
