# -*- coding: utf-8 -*-
"""
Routing (Werkzeug)
==================

:state: stable
:dependencies: Werkzeug_
:feature: `routing`

This extension implements routing via werkzeug.routing_.

.. _Werkzeug: http://werkzeug.pocoo.org
.. _werkzeug.routing: http://werkzeug.pocoo.org/documentation/dev/routing.html

Configuration
-------------

The extension is configured with a simple dictionary where keys are paths to
the modules that contain routing rules, and values define mounting points
(prefixes) for the resulting URL maps. If the value is `null`, then it is
assumed that the rules are mounted to the root.

Example (YAML)::

    tool.ext.werkzeug_routing.Routing:
        foo.views: /foo/
        bar.views: /
        quux.views: null

In the above example the routing rules exported by both `bar.Bar` and
`quux.Quux` are mounted to the root, while the rules provided by `foo.Foo` are
submounted to ``/foo/``.

API reference
-------------
"""

import logging

from werkzeug.routing import *
from werkzeug import redirect, Request, responder
from tool import local, app
from tool.application import request_ready
from tool.importing import import_whatever
from tool.routing import BaseRoutingPlugin  # TODO: move that code, too


logger = logging.getLogger(__name__)


class RoutingMiddleware(object):
    def __init__(self, application):
        self.app = application

    def __call__(self, environ, start_response):
        plugin = app.get_feature(Routing.features)

        # create request object
        request = Request(environ)
        logger.debug('Got new request object')

        local.request = request

        request_ready.send(sender=request, request=request)

        # bind URLs
        plugin.env['urls'] = plugin.env['url_map'].bind_to_environ(environ)
        #urls_bound.send(sender=self, map_adapter=self.urls)

        # determine current URL, find and call corresponding view function
        # another approach: http://stackoverflow.com/questions/1796063/werkzeug-mapping-urls-to-views-via-endpoint
        logger.debug('Dispatching the request')


        result = plugin.env['urls'].dispatch(plugin._find_and_call_view,
                                             catch_http_exceptions=True)
        #except NotFound:
        #    return self.app()(environ, start_response)
        return result(environ, start_response)


class Routing(BaseRoutingPlugin):
    "Werkzeug routing plugin for Tool."

    features = 'routing'

    def make_env(self, **kwargs):
        url_map = Map()
        for module, mountpoint in kwargs.iteritems():
            self._add_urls(url_map, module, submount=mountpoint)

        return {
            'url_map': url_map,
            'urls': None,
        }

    def get_middleware(self):
        return [(RoutingMiddleware, (), {})]

    def _find_and_call_view(self, endpoint, v):
        logger.debug('Looking up the view for endpoint {0}'.format(endpoint))
        if isinstance(endpoint, basestring):
            try:
                endpoint = import_attribute(endpoint)
            except ImportError as e:
                raise ImportError('Could not import view "%s"' % endpoint)
        assert hasattr(endpoint, '__call__')
        logger.debug('Calling view {0}.{1}'.format(endpoint.__module__,
                                                   endpoint.__name__))
        return endpoint(local.request, **v)

    def compile_rule(self, string, **kwargs):
        """Returns a list of :class:`werkzeug.routing.Rule` objects based on
        given view's attribute `routing_rules` as populated by the
        :func:`~tool.routing.url` decorator.

        Rules are not compiled there because at the moment when function is
        being decorated it is usually not yet known which routing library is
        going to be used.
        """
        return Rule(string, **kwargs)

    def url_for(self, endpoint, **kwargs):
        try:
            return self.env['urls'].build(endpoint, kwargs)
        except BuildError:
            if isinstance(endpoint, basestring):
                # we store callable endpoints, so try importing
                endpoint = import_whatever(endpoint)
            return self.env['urls'].build(endpoint, kwargs)

    def redirect_to(self, endpoint, **kwargs):
        url = self.url_for(endpoint, **kwargs)
        return redirect(url)

    def _add_urls(self, url_map, rules, submount=None):
        ### For routes: see http://routes.groovie.org/setting_up.html#submappers

        logger.debug('Adding URLs {0}'.format(rules))

        if not hasattr(rules, '__iter__'):
            rules = self.find_urls(rules)
        if submount:
            assert isinstance(submount, basestring)
            url_map.add(Submount(submount, rules))
        else:
            for rule in rules:
                url_map.add(rule)
        return url_map

    def add_urls(self, rules, submount=None):
        """
        :param rules:
            list of rules or dotted path to module where the rules are exposed.
        :param submount:
            (string) prefix for the rules
        """
        if self.env['urls']:
            raise RuntimeError('Cannot add URLs: the URL map is already bound '
                               'to environment.')
        self._add_urls(self.env['url_map'], rules, submount)
