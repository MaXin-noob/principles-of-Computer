"""
Static files
============

.. warning::

    TODO: rewrite


        Exposes all files in given directory using given rule. By default all
        files (recursively) are made available with prefix `/media/`.

        The simplest example::

            app.add_files('pictures')

        If you have the file `pictures/image123.jpg`, it will be accessible at
        the URL `http://localhost:6060/media/pictures/image123.jpg`. Note that
        the resulting URL is automatically prefixed with "media" to avoid
        clashes with other URLs.

        To specify custom URLs (especially if you are adding multiple
        directories) provide the relevant rules, e.g.::

            # ./pictures/image123.jpg --> http://localhost/images/image123.jpg
            app.add_files('pictures', '/images')

            # ./text/report456.pdf --> http://localhost/text/report456.pdf
            app.add_files('docs', '/text')

        The path to directory can be either absolute or relative to the
        project.

        To build a URL, type::

            app.urls.build('media:pictures', {'file': 'image123.jpg'})

        (The `media:` prefix is added automatically; if will not be present if
        you specify custom `endpoint` param or if the innermost directory in
        the path is named "media".)

"""

import logging
import os
from werkzeug import SharedDataMiddleware
from werkzeug.routing import Rule
from tool.plugins import BasePlugin


logger = logging.getLogger(__name__)


class StaticFiles(BasePlugin):
    requires = ['{routing}']

    def make_env(self, **paths):
        routing = self.app.get_feature('routing')
        middleware_rules = []  #[{rule: path+'/'}]
        for path, conf in paths.iteritems():
            logger.debug('Adding files {0}'.format(path))

            rule, endpoint = self._get_rule_and_endpoint(path, **conf or {})

            placeholder_url = self._get_placeholder_rule(rule, endpoint)
            routing.add_urls([placeholder_url])

            middleware_rules.append({rule: path+'/'})

        return {'middleware': [(SharedDataMiddleware, middleware_rules, {})]}

    def get_middleware(self):
        return self.env['middleware']

    def get_routing(self):
        return self.env['urls']

    def _get_rule_and_endpoint(self, path, rule=None, endpoint=None):

        innermost_dir = os.path.split(path)[-1].lstrip('./')

        ## Serving the files

        # generate rule (just take the innermost directory name and prefix it
        # with "media" if it's not already named so)
        if not rule:
            template = u'/{0}/' if innermost_dir == 'media' else u'/media/{0}/'
            rule = template.format(innermost_dir)

        # generate unique (and transparent) endpoint
        if not endpoint:
            template = u'{0}' if innermost_dir == 'media' else u'media:{0}'
            endpoint = template.format(innermost_dir)

        if isinstance(rule, unicode):
            # workaround for SharedDataMiddleware: it will break trying
            # expression "path.startswith(search_path)" if `path` is
            # unicode and `search_path` is a non-ascii str.
            # In general, URLs are considered plain non-Unicode strings.
            rule = rule.encode('utf-8')

        return rule, endpoint

    def _get_placeholder_rule(self, rule, endpoint):
        ## Building the URL

        # make sure we can build('media:endpoint', {'file':...})
        if not '<file>' in rule:
            rule = rule.rstrip('/') + '/<file>'

        # create a fake URL so that MapAdapter.build works as expected
        return Rule(rule, endpoint=endpoint, build_only=True)


    # TODO: extract this to a plugin (e.g. tool.ext.staticfiles)
    # other plugins may require it to be configured and then use its own API to
    # contribute to routing and middleware. The plugin can be the canonic
    # implementation with an abstract identity, so a custom implementation can
    # be dropped in replacing the default one.
    '''
    def add_files(self, path, rule=None, endpoint=None):
        """
        Exposes all files in given directory using given rule. By default all
        files (recursively) are made available with prefix `/media/`.

        The simplest example::

            app.add_files('pictures')

        If you have the file `pictures/image123.jpg`, it will be accessible at
        the URL `http://localhost:6060/media/pictures/image123.jpg`. Note that
        the resulting URL is automatically prefixed with "media" to avoid
        clashes with other URLs.

        To specify custom URLs (especially if you are adding multiple
        directories) provide the relevant rules, e.g.::

            # ./pictures/image123.jpg --> http://localhost/images/image123.jpg
            app.add_files('pictures', '/images')

            # ./text/report456.pdf --> http://localhost/text/report456.pdf
            app.add_files('docs', '/text')

        The path to directory can be either absolute or relative to the
        project.

        To build a URL, type::

            app.urls.build('media:pictures', {'file': 'image123.jpg'})

        (The `media:` prefix is added automatically; if will not be present if
        you specify custom `endpoint` param or if the innermost directory in
        the path is named "media".)

        """
        logger.debug('Adding files {0}'.format(path))

        innermost_dir = os.path.split(path)[-1].lstrip('./')

        ## Serving the files

        # generate rule (just take the innermost directory name and prefix it
        # with "media" if it's not already named so)
        if not rule:
            template = u'/{0}/' if innermost_dir == 'media' else u'/media/{0}/'
            rule = template.format(innermost_dir)

        # generate unique (and transparent) endpoint
        if not endpoint:
            template = u'{0}' if innermost_dir == 'media' else u'media:{0}'
            endpoint = template.format(innermost_dir)

        # set up the middleware
        from werkzeug import SharedDataMiddleware
        self.wrap_in(SharedDataMiddleware, {rule: path+'/'})

        ## Building the URL

        # make sure we can build('media:endpoint', {'file':...})
        if not '<file>' in rule:
            rule = rule.rstrip('/') + '/<file>'

        # add fake URL so that MapAdapter.build works as expected
        self.add_urls([Rule(rule, endpoint=endpoint, build_only=True)])
    '''

