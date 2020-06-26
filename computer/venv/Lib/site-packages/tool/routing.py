# -*- coding: utf-8 -*-

"""
URL routing
===========

The whole task of defining and dispatching of URLs is perfectly managed by
Werkzeug.

Tool wraps Werkzeug's routing machinery and provides a few new convenience
features:

* decorator :func:`url`
* function :func:`url_for`
* function :func:`find_urls`
* function :func:`redirect_to`

All the rest is imported straight from Werkzeug.

.. seealso::

    this document represents all Tool-specific objects and a subset of
    those available in Werkzeug. Please read the original `Werkzeug routing`_
    reference for complete documentation.

.. _Werkzeug routing: http://werkzeug.pocoo.org/documentation/dev/routing.html

Overview
--------

In short, you should:

1. create some "views" (functions to be called when the user requests URLs);
2. create a :class:`Map` instance;
3. add :class:`rules <Rule>` to the map so that URL patterns are linked to the
   "views" (these views become "endpoints");
4. Bind the map to environment (:class:`~tool.application.ApplicationManager`
   will do that for you);
5. trigger the dispatcher to define which endpoint corresponds to given URL.
   This happens automatically if you create and run a WSGI application using
   :class:`~tool.application.ApplicationManager`.

It is also possible to build a URL when you know the endpoint and the keywords
that make sense for certain rule. See :func:`url_for`.

The easiest way to create rules for views is with decorator :func:`url`.

The easiest way to gather a list of rules for all views defined in given module
is with function :func:`find_urls`.

See :doc:`application` for more details on how to build URL maps and include
the rules into an application. It's always a good idea for a pluggable bundle
to only define the rules, and for the application manager to actually gather
them from different bundles and mount as needed.

API reference
-------------
"""
import sys
from tool import app
from tool.plugins import BasePlugin
from tool.importing import import_module, import_whatever


__all__ = [
    # defined here
    'url', 'url_for', 'find_urls', 'redirect_to',
    # defined in werkzeug.routing
    'Map', 'MapAdapter', 'Rule', 'Subdomain', 'Submount', 'redirect'
]


class BaseRoutingPlugin(BasePlugin):

    features = 'routing'

    def compile_rule(self, string, **kwargs):
        """Returns a list of native rule objects based on given view's
        attribute `routing_rules` as populated by the :func:`~tool.routing.url`
        decorator.

        Rules are not compiled there because at the moment when function is
        being decorated it is usually not yet known which routing library is
        going to be used.
        """
        raise NotImplementedError

    def find_urls(self, source):
        """
        Accepts either module or dictionary.

        Returns a cumulative list of rules for all members of given module or
        dictionary.

        How does this work? Any callable object can provide a list of rules as
        its own attribute named ``url_rules``.  The ``url`` decorator adds such
        an attribute to the wrapped object and sets the object as endpoint for
        rules being added. ``find_urls``, however, does not care about
        endpoints, it simply gathers rules scattered all over the place.

        Usage::

            from tool.routing import Map, Submount
            import foo.views

            # define a view exposed at given URL. Note that it is *not* a good idea
            # to mix views with configuration and management code in real apps.
            @url('/hello/')
            def hello(request):
                return 'Hello!'

            # gather URLs from this module (yields the "hello" one)
            local_urls = find_urls(locals())

            # gather URLs from some bundle's views module
            foo_urls = find_urls(foo.views)

            # gather URLs from a module that is not imported yet
            bar_urls = find_urls('bar.views')

            url_map = Map(
                local_urls + [
                    Submount('/foo/', foo_urls),
                    Submount('/bar/', bar_urls),
                ]
            )

            # ...make app, etc.

        Such approach does not impose any further conventions (such as where to
        place the views) and leaves it up to you whether to store URL mappings
        and views in separate modules or keep them together using the ``url``
        decorator. It is considered good practice, however, to not mix
        different things in the same module.
        """
        if isinstance(source, dict):
            d = source
        else:
            if isinstance(source, basestring):
                source = import_module(source)
            d = dict((n, getattr(source, n)) for n in dir(source))

        def generate(d):
            for name, attr in d.iteritems():
                if hasattr(attr, '__call__') and hasattr(attr, 'routing_rules'):
                    if hasattr(attr.routing_rules, '__are_you_too_smart__'):
                        # workaround for "too smart" objects like pymongo's
                        # Database instances that always return True for
                        # hasattr() but the values turn out to be unexpected
                        # (i.e. a Collection object instead of a list)
                        continue
                    for rule_draft in attr.routing_rules:
                        yield self.compile_rule(**rule_draft)
        return list(generate(d))

    def redirect_to(self, endpoint):
        raise NotImplementedError

    def decorate_view(self, func, string, kwargs):
        raise NotImplementedError


def redirect_to(endpoint, **kwargs):
    """
    A wrapper for :func:`redirect`. The difference is that the endpoint is
    first resolved via :func:`url_for` and then passed to :func:`redirect`.
    """
    plugin = app.get_feature(BaseRoutingPlugin.features)
    return plugin.redirect_to(endpoint, **kwargs)

def url(string=None, **kwargs):
    """
    Decorator for web application views. Marks given function as bindable to
    the given URL.

    Basically it is equivalent to the decorator ``expose`` of CherryPy, however
    we don't try to infer the rule from function signature; instead, we only
    support the easiest case (URL is equal to function name) and require the
    rule to be explicitly defined when the function accepts arguments (apart
    from the request object which is always the first argument).


    Usage::

        @url()                # rule not defined, inferred from function name
        def index(request):
            return 'hello'

        @url('/index/')       # same rule, defined explicitly
        def index(request):
            return 'hello'

        @url('/page/<int:page_id>/')
        def page(request, page_id):     # extra args, rule is *required*
            return 'page #%d' % page_id

    The above is roughly same as::

        def index(request):
            return 'hello'
        index.url_rules = [werkzeug.Rule('/index/', endpoint=index)]

    ...and so on.

    The ``url`` decorators can be chained so that the view function is
    available under different URLs::

        @url('/archive/')
        @url('/archive/<int(4):year>/')
        @url('/archive/<int(4):year>/<int(2):month>/')
        def archive(request, **kwargs):
            entries = Entry.objects(db).where(**kwargs)
            return ', '.join(unicode(e) for e in entries)

    """
#        if 'endpoint' in kw:
#            raise NameError('Endpoint must not be defined explicitly when '
#                            'using the @url decorator.')
#        kw['endpoint'] = view    # = view.__name__
#
#        # infer URL from function name (only simple case without kwargs)
#        if not string and 1 < view.__code__.co_argcount:
#            raise ValueError('Routing rule must be specified in the @url '
#                             'decorator if the wrapped view function '
#                             'accepts more than one argument.')
#        kw['string'] = string or '/{0}/'.format(view.__name___)
#        view.url_rules = getattr(view, 'url_rules', [])
#        view.url_rules.append(Rule(**kwargs))
#        return view

    def inner(view):
        kwargs['endpoint'] = view    # = view.__name__
        # infer URL from function name (only simple case without kwargs)
        if not string and 1 < view.__code__.co_argcount:
            raise ValueError('Routing rule must be specified in the @url '
                             'decorator if the wrapped view function '
                             'accepts more than one argument.')
        kwargs['string'] = string or '/{0}/'.format(view.__name___)
        view.routing_rules = getattr(view, 'routing_rules', [])
        view.routing_rules.append(kwargs)
        return view
    return inner

def url_for(endpoint, **kwargs):
    """
    Given the endpoint and keyword arguments, builds and returns the URL.

    :param endpoint:
        either a callable object, or a string representing the dotted path to
        such object (e.g. ``myapp.views.list_entries``)

    The keywords are passed to :meth:`MapAdapter.build`.
    """
    plugin = app.get_feature(BaseRoutingPlugin.features)
    return plugin.url_for(endpoint, **kwargs)
