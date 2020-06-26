# -*- coding: utf-8 -*-
"""
Web Admin
=========

:state: beta
:dependencies: `Doqu`_

Administrative interface for `Doqu`_. Requires :mod:`tool.ext.documents` to be
properly set up.

Complete configuration example (see :doc:`application` for details)::

    extensions:
        tool.ext.admin.AdminWeb: null
        tool.ext.werkzeug_routing.Routing:
            tool.ext.admin.views: /admin/

.. _Doqu: http://pypi.python.org/pypi/doqu

"""
import os

from doqu import Document
from copy import deepcopy
from functools import wraps
from tool import app
from tool.plugins import BasePlugin


DEFAULT_NAMESPACE = 'main'


class AdminWeb(BasePlugin):

    requires = ('{document_storage}', '{templating}',
                '{routing}', '{breadcrumbs}')

    features = 'admin'

    # admin-specific; non thread-local
    registry = {
        'registered_models': {},
        'urls_for_models': {},
        'excluded_names': {},
        'ordering': {},
        'list_names': {},
        'search_names': {},
    }

    def make_env(self):
        templating = self.app.get_feature('templating')
        templating.register_templates(__name__)

        # TODO: support templating backends other than Jinja (just rename key?)
        templating.update_template_context(dict(
            admin_url_for = self.admin_url_for,
            admin_url_for_query = self.admin_url_for_query,
        ))

        # register generic Document — can be unregistered later by hand
        register(Document)

        env = deepcopy(self.registry)

        return dict(env,
            default_namespace=DEFAULT_NAMESPACE
        )

    def admin_url_for_query(self, query, namespace=None):
        """
        Returns admin URL for given document query. Usage (in templates)::

            <a href="{{ admin_url_for_query(object_list) }}">View in admin</a>

        :param query:
            A doqu query adapter instance. The related document class must be
            already registered with admin.
        :param namespace:
            The admin namespace (optional).

        """
        namespace = namespace or self.env['default_namespace']
        model_name = query.doc_class.__name__
        t = self.app.get_feature('routing')
        return t.url_for('tool.ext.admin.views.object_list',
                         namespace=namespace, model_name=model_name)

    def admin_url_for(self, obj, namespace=None):
        """
        Returns admin URL for given object. Usage (in templates)::

            <a href="{{ admin_url_for(obj) }}">View {{ obj.title }} in admin</a>

        :param obj:
            A doqu.Document instance. Must have the primary key. The document class
            must be already registered with admin.
        :param namespace:
            The admin namespace (optional).

        """
        namespace = namespace or plugin.env['default_namespace']
        model_name = obj.__class__.__name__
        t = app.get_feature('routing')
        return t.url_for('tool.ext.admin.views.object_detail',
                         namespace=namespace, model_name=model_name, pk=obj.pk)

def register(model, namespace=DEFAULT_NAMESPACE, url=None, exclude=None,
             ordering=None, list_names=None, search_names=None):
    """
    :param model:
        a Doqu document class
    :param namespace:
        a short string that will be part of the URL. Default is "main".
    :param url:
        a function that gets a model instance and returns an URL
    :param ordering:
        a dictionary in this form: ``{'names': ['foo'], 'reverse': False}``.
        See Docu query API for details on ordering.
    :param list_names:
        a list of field names to be displayed in the list view.
    :param search_names:
        a list of field names by which to search.

    Usage::

        from doqu import Document
        from tool.ext import admin
        from tool import app

        class Item(Document):
                ...
        admin.register(Item)

    """
    # TODO: model should provide a slugified version of its name itself
    name = model.__name__ #.lower()

    r = AdminWeb.registry

    r['registered_models'].setdefault(namespace, {})[name] = model
    r['urls_for_models'][model] = url
    r['excluded_names'][model] = exclude
    r['ordering'][model] = ordering
    r['list_names'][model] = list_names
    r['search_names'][model] = search_names

    return model


class DocAdmin(object):
    """
    Description of admin interface for given Document class.
    """
    namespace = DEFAULT_NAMESPACE
    url = None
    exclude = None
    order_by = None
    ordering_reversed = False
    list_names = None
    search_names = None

    @classmethod
    def register_for(cls, doc_class):
        if cls.order_by:
            ordering = dict(names=cls.order_by, reverse=cls.ordering_reversed)
        else:
            ordering = None
        register(doc_class,
            namespace = cls.namespace,
            url = cls.url,
            exclude = cls.exclude,
            ordering = ordering,
            list_names = cls.list_names,
            search_names = cls.search_names,
        )


def register_for(doc_class):
    """
    Decorator for DocAdmin classes. Usage::

        @admin.register_for(Note)
        class NoteAdmin(admin.DocAdmin):
            namespace = 'notepad'
            url = lambda d: d.get_url()
            exclude = ['foo']
            ordering = {'names': ['date_time'], 'reverse': True}

    """
    @wraps(doc_class)
    def inner(admin_class):
        admin_class.register_for(doc_class)
        return admin_class
    return inner
