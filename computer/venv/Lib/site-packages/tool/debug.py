# -*- coding: utf-8 -*-

"""
Debugging utilities
===================

Werkzeug provides excellent `debugging features`_. This module only provides a
few wrappers for easier coupling of these features with the Tool API.

.. _debugging features: http://werkzeug.pocoo.org/documentation/dev/test.html

"""

from werkzeug import BaseResponse, Client
from tool.cli import Fore, Back, Style
from tool import app


__all__ = ['client_factory', 'print_url_map', 'print_wsgi_stack']


# http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
#COLOR_BLUE   = '\033[94m'
#COLOR_GREEN  = '\033[92m'
#COLOR_YELLOW = '\033[93m'
#COLOR_RED    = '\033[91m'
#COLOR_ENDC   = '\033[0m'

COLOR_WARNING = Fore.YELLOW
COLOR_FAIL    = Fore.RED


def print_url_map(url_map):
    """
    Pretty-prints given URL map (must be a werkzeug.routing.Map).
    """
    def get_endpoint_repr(endpoint):
        if hasattr(endpoint, '__call__'):
            return u'%s.%s' % (endpoint.__module__, endpoint.__name__)
        return endpoint
    print
    print ' URLS:'
    if not url_map._rules:
        print '   (the URL map does not contain any rules.)'
        print
        return
    import re
    rule_labels = [''.join([Fore.YELLOW, unicode(rule), Fore.RESET])
                   for rule in url_map._rules]
    max_len = max(len(label) for label in rule_labels)
    for rule, rule_label in zip(url_map._rules, rule_labels):
#        rule_label = ''.join([Fore.YELLOW, unicode(rule), Fore.RESET])
#        rule_label = re.sub('([^/]+)',
#        rule_label = re.sub('<([^:]+:)?(.+?)>',
##        rule_label = re.sub('<(([^:>]+:)?)(.+?)>',
#                            r'{0}\1{1}'.format(Style.BRIGHT, Style.NORMAL),
#                            #r'<\1{0}\2{1}>'.format(Style.BRIGHT, Style.NORMAL),
#                            rule_label)
        endpoint_repr = get_endpoint_repr(rule.endpoint)
        endpoint_label = ''.join([Fore.GREEN, endpoint_repr, Fore.RESET])
        arguments = ''
        if rule.arguments:
            arguments = '{0}({1}){2}'.format(
                Style.DIM, ', '.join(rule.arguments), Style.NORMAL)
        print '   {rule:.<{width}} {endpoint} {arguments}'.format(
            rule = rule_label,
            width = max_len + 2,# + len(Fore.YELLOW+Fore.RESET) + 2,
            endpoint = endpoint_label,
            arguments = arguments,
        )
    print

def print_wsgi_stack(stack):
    """
    Pretty-prints an :class:`~tool.ApplicationManager` instance's current WSGI
    stack. The list of middleware is printed in the order in which the
    request/dispatch/response flow actually goes, i.e. ingress (shown in
    green), URL/view routing (yellow) and egress (blue). The completeness of
    the list depends on how early the function is called.

    Usage::

        app_manager = tool.ApplicationManager()
        app_manager.wrap_in(YourFavouriteMiddleware)
        print_wsgi_stack(app_manager.wsgi_stack)

    """
    print 'Managed WSGI stack:'
    ingress = True
    print(' request')
    for i, item in enumerate(stack + [None] + list(reversed(stack))):
        if item:
            color = (COLOR_GREEN if ingress else COLOR_BLUE)
            print(' ↳ '+  color + item[0].__name__ + COLOR_ENDC)
        else:
            ingress = False
            print(' ↳ '+ COLOR_YELLOW +'Routing (URL→view)'+ COLOR_ENDC)
            print(' response')
    print


class ClientResponse(BaseResponse):
    pass


def client_factory():
    """
    Creates and returns a :class:`werkzeug.Client` instance bound to the
    application manager. Allows to send requests to the application. Can be
    used both in automated tests and in the interactive shell.

    Usage::

        from tool.debug import client_factory
        c = client_factory()
        r = c.get('/')
        print r.data

    See Werkzeug documentation, section `debug` for details.
    """
    return Client(app, response_wrapper=ClientResponse)
