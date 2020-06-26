# -*- coding: utf-8 -*-
"""
Authentication and identification
=================================

:state: beta
:dependencies: Doqu_, repoze.who_

This bundle integrates Tool with repoze.who_, a powerful and extremely
configurable identification and authentication framework.

The extension provides:

* sensible default configuration presets;
* authenticator and metadata provider that let you store user accounts as Doqu_
  documents;
* automatic registration of the middleware in
  :class:`tool.application.ApplicationManager`;
* a protective decorator for views (:func:`requires_auth`) that ensures that
  the view is only available for authenticated users;
* an easy way to access the user account document from any place of your
  application (the :func:`get_user` function).

.. _repoze.who: http://docs.repoze.org/who/2.0/
.. _Doqu: http://pypi.python.org/pypi/doqu

You can choose between two commonly used configuration presets. You can also
safely ignore both and configure repoze.who as desired (see `custom_config`).

Bundle configuration:

* ``secret`` is a random string that is used to sign certain auth methods.
* ``preset`` — name of the preset to use (see list of available presets below).
  Ignored if `config` if specified.
* ``config`` — dotted path to a dictionary (or a callable that returns
  the dictionary) with custom configuration for the
  PluggableAuthenticationMiddleware. Note that the callable configurator will
  be called the bundle configuration dictionary.

Available presets:

* "basic" — sets up Basic Access Authentication (:rfc:`2617`).
* "form" — sets up the "auth ticket" protocol and a HTTP form for
  identification, authentication and challenge.

Configuration examples
----------------------

Basic authentication preset (in YAML, unrelated settings omitted)::

    tool.ext.who:
        preset: 'basic'

This is enough for basic authentication to work. Note that the credentials are
compared against :class:`~tool.ext.who.User` instances, so make sure you
have at least one user in the database. You can create one in the shell::

    $ ./manage.py shell
    >>> from tool.ext.who import User
    >>> user = User(username='john')
    >>> user.set_password('my cool password')  # will be encrypted
    >>> user.save(context.docu_db)

Here we go, the user can now log in and his account object will be available
via :func:`get_user`. You can also try the "form" preset for better integration
with website design.

However, the presets are obviously useless for certain cases. You can always
fine-tune the repoze.who middleware as if you would do without Tool.

An example of custom PluggableAuthenticationMiddleware configuration::

    tool.ext.who:
        config: 'myproject.configs.who'

Here it is supposed that your custom configuration is composed according to the
repoze.who middleware documentation (as keywords) and stored in the module
`myproject.configs` like this::

    who = {
        'identifiers': [('basic_auth', basic_auth)],
        …
    }

API reference
-------------
"""
import logging
logger = logging.getLogger('tool.ext.who')

# 3rd-party
from repoze.who.middleware import PluggableAuthenticationMiddleware

# tool
from tool.signals import called_on
from tool.importing import import_whatever
from tool.plugins import BasePlugin
#    FIXME let user configure databases per bundle:
from tool.ext.documents import storages, default_storage

# this bundle
from schema import User
from views import render_login_form
from presets import KNOWN_PRESETS
from shortcuts import get_user
from decorators import requires_auth


__all__ = ['requires_auth', 'get_user', 'User']


class AuthenticationPlugin(BasePlugin):

    features = 'authentication'
    requires = ('{document_storage}',)

    def make_env(self, **settings):
        if 'secret' not in settings:
            # TODO: add tool.conf.ConfigurationError excepton class
            raise KeyError('Plugin {0} requires setting "secret"'.format(__name__))

        db_label = settings.pop('database', None)
        database = storages.get(db_label) or default_storage()

        if settings.get('config'):
            conf = import_whatever(settings['config'])
            mw_conf = conf(**settings) if hasattr(conf, '__call__') else conf
        else:
            preset = settings.get('preset', 'basic')
            f = KNOWN_PRESETS[preset]
            mw_conf = f(**settings)

        return {
            'middleware_config': mw_conf,
            'database': database,
        }

    def get_middleware(self):
        kwargs = self.env['middleware_config']
        logger.debug('who conf: {0}'.format(kwargs))
        return [
            (PluggableAuthenticationMiddleware, [], kwargs),
        ]

'''
#@called_on(app_manager_ready)
def setup_auth(sender, **kwargs):
    """
    Sets up a sensible default configuration for repoze.who middleware. Called
    automatically when the application manager is ready.
    """
    logger.debug('Setting up the bundle...')

    bundle_conf = sender.get_settings_for_bundle(__name__)

    if 'secret' not in bundle_conf:
        # TODO: add tool.conf.ConfigurationError excepton class
        raise KeyError('Bundle auth_who requires setting "secret"')

    if bundle_conf.get('config'):
        conf = import_whatever(bundle_conf['config'])
        mw_conf = conf(**bundle_conf) if hasattr(conf, '__call__') else conf
    else:
        preset = bundle_conf.get('preset', 'basic')
        f = KNOWN_PRESETS[preset]
        mw_conf = f(**bundle_conf)

    sender.wrap_in(PluggableAuthenticationMiddleware, **mw_conf)
'''
