# -*- coding: utf-8 -*-
"""
Authorization
=============

:state: alpha
:dependencies: Docu_, repoze.who_, repoze.what_

This bundle integrates Tool with repoze.what_, a powerful and configurable
authorization framework.

Object-level ("row-level") permissions are not supported neither by this bundle
nor by repoze.what itself, nor by any known related project. Please drop me a
message if you have an idea on how to implement this feature.

Basic usage example::

    from tool.ext.what import require, is_admin

    @require(is_admin())
    def some_secret_view(request):
        return u'Secret text!'

.. _repoze.who: http://docs.repoze.org/who/
.. _repoze.what: http://docs.repoze.org/what/
.. _Docu: http://pypi.python.org/pypi/docu

API reference
-------------

.. automodule:: tool.ext.what.predicates
   :members:
"""

import logging
logger = logging.getLogger('tool.ext.what')

# tool
from tool.signals import called_on
from tool.importing import import_whatever
from tool.plugins import BasePlugin

# this bundle
#from schema import User
#from views import render_login_form
#from presets import KNOWN_PRESETS
#from shortcuts import get_user
from decorators import require
from predicates import *
from schema import Group, Member
from adapters import *


#__all__ = ['require']


class AuthorizationPlugin(BasePlugin):
    requires = ('tool.ext.who',)
    def get_middleware(self):
        return RepozeWhatAdapterMiddleware, (), {}


#@called_on(app_manager_ready)
def setup_auth(sender, **kwargs):
    """
    Wraps the WSGI application into the repoze.what middleware.
    Sets up a sensible default configuration for repoze.who middleware. Called
    automatically when the application manager is ready.
    """
    logger.debug('Setting up the bundle...')
    sender.wrap_in(RepozeWhatAdapterMiddleware)

def RepozeWhatAdapterMiddleware(app):  # PEP-8 ?
    """
    Add authentication and authorization middleware to the ``app``.

    :param app: The WSGI application.
    :return: The same WSGI application, with authentication and
        authorization middleware.

    People will login using HTTP Authentication and their credentials are
    kept in an ``Htpasswd`` file. For authorization through repoze.what,
    we load our groups stored in an ``Htgroups`` file and our permissions
    stored in an ``.ini`` file.

    """

    from repoze.who.plugins.basicauth import BasicAuthPlugin
    from repoze.who.plugins.htpasswd import HTPasswdPlugin, crypt_check

    from repoze.what.middleware import setup_auth

    # Defining the group adapters; you may add as much as you need:
    groups = {'all_groups': DocuGroupSourceAdapter()}

    # FIXME Defining the permission adapters; you may add as much as you need:
#    permissions = {'all_perms': INIPermissionsAdapter('/path/to/perms.ini')}
    permissions = {'all_perms': FakePermissionSourceAdapter()}

    # FIXME repoze.who identifiers; you may add as much as you need:
    basicauth = BasicAuthPlugin('Private web site')
    identifiers = [('basicauth', basicauth)]

    # FIXME repoze.who authenticators; you may add as much as you need:
    htpasswd_auth = HTPasswdPlugin('/path/to/users.htpasswd', crypt_check)
    authenticators = [('htpasswd', htpasswd_auth)]

    # FIXME repoze.who challengers; you may add as much as you need:
    challengers = [('basicauth', basicauth)]

    app_with_auth = setup_auth(
        app,
        groups,
        permissions,
        identifiers=identifiers,
        authenticators=authenticators,
        challengers=challengers)
    return app_with_auth
