# -*- coding: utf-8 -*-
"""
Storm ORM
=========

:state: stable
:dependencies: Storm_
:feature: `orm`

Support for Storm_, an object-relational mapper (ORM) for Python developed at
Canonical.

.. _Storm: http://storm.canonical.com

:dependencies: `storm`

Configuration
-------------

Example configuration (YAML)::

    tool.ext.storm_orm.Storm:
        uri: "sqlite:"

Usage
-----

Example usage::

    from tool import app

    joe = Person()
    joe.name = 'Joe'

    orm = app.get_feature('orm')

    orm.db.add(joe)
    orm.db.find(Person, Person.name=='Joe').one()

See the `Storm tutorial`_ for details. Just replace ``store`` with ``orm.db``
and here you are.

.. _Storm tutorial: http://storm.canonical.com/Tutorial

API reference
-------------
"""
from storm.locals import *

from tool.plugins import BasePlugin


class Storm(BasePlugin):
    """Adds the ORM feature.

    Required configuration options:

    :param uri:
        a string describing the connection, as follows:
        ``scheme://username:password@hostname:port/database_name``
        (see `creating database`_ in tutorial).

    .. _creating database: http://storm.canonical.com/Tutorial#Creating%20a%20database%20and%20the%20store
    """
    features = 'orm'

    def make_env(self, uri):
        database = create_database("sqlite:")
        store = Store(database)
        return {'store': store}

    @property
    def db(self):
        """The :class:`storm.locals.Store` instance, as configured here by
        :class:`tool.application.Application`.
        """
        try:
            return self.env['store']
        except KeyError:
            raise RuntimeError('Connection to DB is missing.')
