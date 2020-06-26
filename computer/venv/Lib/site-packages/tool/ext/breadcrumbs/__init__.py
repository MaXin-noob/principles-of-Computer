# -*- coding: utf-8 -*-
"""
Breadcrumbs
===========

TODO: better documentation

In templates::

    {{ get_breadcrumb_title('/foo/bar/') }}

Or even better::

    {{ get_breadcrumb_trail() }}

"""

__all__ = ['entitled']


from functools import wraps
import logging
import werkzeug
from tool import app
from tool.context_locals import request
from tool.plugins import BasePlugin
from tool.signals import called_on


logger = logging.getLogger(__name__)


BREADCRUMB_ATTR_NAME = 'breadcrumb'


def entitled(name_source):
    """
    Decorator. Sets `name_source` as the breadcrumb name source for given view
    function.

    :param name_source:
        An arbitrary object. If callable, must accept the same arguments as the
        view function itself (except for the request object). If not callable,
        must be a Unicode string or at least not fail on `unicode(x)`.

    """
    def inner(view_function):
        setattr(view_function, BREADCRUMB_ATTR_NAME, name_source)
        return view_function
    return inner

def get_title(path=None):
    """
    Resolves the URL to a view function and returns the relevant title. The
    title is either taken from the view function's attribute ``breadcrumb`` (can
    be set with :func:`entitled` or manually) or from the view function's
    ``__name__``.

    :param path:
        The "path" part of a URL (see werkzeug.Request.path). If `None`,
        current URL is used (from context locals).

    """
    routing = app.get_feature('routing')
    assert routing.env['urls'], 'Application must be initialized'
    if path is None or path == '':
        path = request.path
    assert isinstance(path, basestring)
    try:
        func, kwargs = routing.env['urls'].match(path)
    except werkzeug.exceptions.NotFound:
        return u'(ENDPOINT NOT FOUND)'
    except werkzeug.routing.RequestRedirect as e:
        return u'({0})'.format(e.new_url)
    except werkzeug.exceptions.MethodNotAllowed as e:
        # if GET is inadequate for this URL, no need to give it a title
        # XXX ...or not? what if it the title is going to be used for the
        # heading of a page that accepts a non-GET method but then normally
        # displays a form or some confirmation messages?
        return u'(Cannot access this URL with GET)'
    else:
        if hasattr(func, BREADCRUMB_ATTR_NAME):
            name_source = getattr(func, BREADCRUMB_ATTR_NAME)
            if hasattr(name_source, '__call__'):
                return name_source(**kwargs)
            else:
                return unicode(name_source)
        return unicode(func.__name__.replace('_', ' '))

def get_trail_titles(path=None, with_root=True):
    """
    Returns a tuple of URLs and titles for all segments of the URL, i.e. the
    URL "/foo/bar/quux" will be split to "/foo/", "/foo/bar/" and
    "/foo/bar/quux", and the function :func:`get_title` applied to each
    segment.

    :param path:
        The "path" part of a URL. Must be plain slash-delimited string without
        query params (see werkzeug.Request.path). If empty, current URL is used
        (from context locals).
    :param with_root:
        If `False`, the root (``/``) is not included in results. Default if
        `True`.

    """
    if path is None or path == '':
        assert request, 'application must be initialized'
        path = request.path
    assert isinstance(path, basestring)
    parts = path.rstrip('/').split('/')
    if path.endswith('/'):
        parts[-1] += '/'
    urls = ['/'.join(parts[:i+1]) or '/' for i in range(len(parts))]
    urls = [url+'/' if i < len(urls)-1 and not url.endswith('/') else url
            for i, url in enumerate(urls)]
    if not with_root:
        urls.pop(0)
    return [(url, get_title(url)) for url in urls]


class BreadcrumbsPlugin(BasePlugin):
    features = 'breadcrumbs'
    requires = ('{templating}',)

    def make_env(self):
        # XXX it is assumed that Jinja2 is the templating engine. It should be
        # possible to populate other engines' globals.
        logger.debug('Contributing functions to the template environment...')
        templating = app.get_feature('templating')
        templating.update_template_context(dict(
            get_breadcrumb_title = get_title,
            get_breadcrumb_trail = get_trail_titles,
        ))


"""
@called_on(templating_ready)
def add_template_functions(sender, **kw):
    # XXX it is assumed that Jinja2 is the templating engine. It should be
    # possible to populate other engines' globals.
    logger.debug('Contributing functions to the template environment...')
    env = sender
    env.globals.update(
        get_breadcrumb_title = get_title,
        get_breadcrumb_trail = get_trail_titles,
    )
"""
