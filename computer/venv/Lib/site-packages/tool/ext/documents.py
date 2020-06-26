# -*- coding: utf-8 -*-
#
# TODO: allow to assign a storage (label) to each plugin.
#       Either in plugin config or somehow else.
#
#
"""
Document storage
================

:state: stable
:dependencies: `Doqu`_
:feature: `document_storage`

`Doqu`_ is a lightweight Python framework for document databases. It provides a
uniform API for modeling, validation and queries across various kinds of
storages. It's the SQLAlchemy for non-relational databases.

.. _Doqu: http://pypi.python.org/pypi/doqu

Configuration example (in YAML)::

    extensions:
        tool.ext.documents.Documents:
            backend: doqu.ext.tokyo_tyrant
            host: localhost
            port: 1978

Or with defaults::

    extensions:
        tool.ext.documents.Documents: nil

The configuration is not Tool-specific. You can provide whatever keywords and
values Doqu_ itself accepts.

Default backend chosen by Tool is `Shelve`_ and the data is stored in the file
`doqu_shelve.db`. Please note that despite this extension does not require any
packages except for Doqu_ itself, it is also unsuitable for medium to large
volumes of data. However, it offers a simple persistence layer. Please refer to
the `Doqu documentation`_ to choose a more efficient backend (for example,
Tokyo Cabinet or MongoDB).

In short, this is what you will get::

    import datetime
    from tool.ext.documents import db
    from doqu import Document, validators

    class Person(Document):
        structure = {
            'name': unicode,
            'birth_date': datetime.date
        }
        validators = {'name': [validators.required()]}
        defaults = {'birth_date': datetime.date.today}
        labels = {
            'name': _('Full name'),
            'birth_date': _('Birth date'),
        }
        use_dot_notation = True

    john = Person(name='John')

    print john.name

    john.save(db)

    print Person.objects(db).where(name__startswith='J').count()

Also, :doc:`ext_admin` provides an automatically generated web interface for
all your document classes (if you register them).

More details:

* `Doqu documentation`_ (usage examples, tutorial, etc.)
* `Shelve`_ Doqu extension reference
* :doc:`ext_admin` (complete web interface for documents)

.. _Doqu documentation: http://packages.python.org/doqu
.. _Shelve: http://packages.python.org/doqu/ext_shelve.html

API reference
-------------
"""
import logging
logger = logging.getLogger(__name__)

import werkzeug.exceptions

from tool import app
import tool.plugins

from doqu import get_db


__all__ = ['get_object_or_404', 'Documents', 'storages', 'default_storage']


FEATURE = 'document_storage'
DEFAULT_DB_NAME = 'default'
DEFAULTS = {
    'backend': 'doqu.ext.shelve_db',
    'path': 'doqu_shelve.db',
}


class Documents(tool.plugins.BasePlugin):
    """A Tool extension that provides support for Doqu_.
    """
    features = FEATURE

    def make_env(self, **databases):
        logger.debug('Confguring {0} with {1}...'.format(self, databases))
        assert databases
        assert DEFAULT_DB_NAME in databases, (
            'database "{0}" must be configured'.format(DEFAULT_DB_NAME))
        env = {}
        for name, settings in databases.iteritems():
            env[name] = get_db(settings)
        return env

    @property
    def default_db(self):
        "Returns default storage object."
        return self.env[DEFAULT_DB_NAME]


# XXX remove the code below? it's harmless but unnecessary


class StoragesRegistry(object):
    def __getitem__(self, label):
        plugin = app.get_feature(FEATURE)
        if label in plugin.env:
            return plugin.env[label]
        raise KeyError('Unknown document storage "{0}". These storages are '
                       'configured: {1}'.format(label, plugin.env.keys()))
    def get(self, label, default=None):
        try:
            return self[label]
        except KeyError:
            return default
storages = StoragesRegistry()


def get_default_storage():
    "Returns defaut storage instance."
    return storages[DEFAULT_DB_NAME]

def default_storage():
    import warnings
    warnings.warn('default_storage() is deprecated, use get_default_storage() '
                  'or Documents.default_db instead.', DeprecationWarning)
    return get_default_storage()


'''
class DefaultStorageProxy(object):
    """
    Syntactic sugar for get_db(). Usage::

        from tool.ext.documents import db

        def some_view(request):
            return Response(Page.objects(db))

    ...which is just another way to write::

        from tool import context

        def some_view(request):
            return Response(Page.objects(context.docu_db))
    """
    def __getattr__(self, name):
        import warnings
        warnings.warn('StorageProxy is deprecated, use `storages` instead',
                      DeprecationWarning)
        try:
            db = self._get_db()
        except KeyError:
            raise AttributeError('Documents bundle must be set up')
        return getattr(db, name)

    def __eq__(self, other_storage):
        # this is important because otherwise doc.save(db) on existing
        # documents will always reset the primary key and create duplicates.
        db = self._get_db()
        return db == other_storage

    def __len__(self):
        db = self._get_db()
        return len(db)

    def __repr__(self):
        db = self._get_db()
        return '<{cls} for {backend}>'.format(
            cls=self.__class__.__name__, backend=db.__module__)

    def _get_db(self):
        return storages[DEFAULT_DB_NAME]
#        conf = context.app_manager.live_conf[__name__]
#        return conf[DEFAULT_DB_NAME]


db = DefaultStorageProxy()
'''

def get_object_or_404(model, **conditions):
    """
    Returns a Docu model instance that ................................................
    """
    db = default_storage()
    qs = model.objects(db).where(**conditions)
    if not qs:
        raise werkzeug.exceptions.NotFound
    if 1 < len(qs):
        raise RuntimeError('multiple objects returned')
    return qs[0]

'''
#@called_on(app_manager_ready)
def setup(**kwargs):
    """
    Setup the ApplicationManager to use Docu.
    """
    logger.debug('Setting up the bundle...')

    manager = kwargs['sender']

    try:
        conf = manager.get_settings_for_bundle(__name__, DEFAULTS)
    except KeyError:
        return False
    live_conf = context.app_manager.live_conf[__name__]
    live_conf[DEFAULT_DB_NAME] = get_db(conf)
'''
