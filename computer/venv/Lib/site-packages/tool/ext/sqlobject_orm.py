# -*- coding: utf-8 -*-
"""
SQLObject ORM
=============

:state: stable
:dependencies: SQLObject_
:feature: `orm`

Support for SQLObject_, a popular Object Relational Manager for providing an
object interface to your database, with tables as classes, rows as instances,
and columns as attributes.

.. _SQLObject: http://sqlobject.org

Configuration
-------------

Example configuration (YAML)::

    tool.ext.sqlobject_orm.SQLObjectExtension:
        uri: "sqlite:/:memory:"

Usage
-----

Example usage::

    from sqlobject import *
    from tool import app

    orm = app.get_feature('orm')

    # declare the model
    class Person(SQLObject):
        name = StringCol()

    # create database
    orm.db.createEmptyDatabase()

    # create table
    Person.createTable()

    # create row
    Person(name="John")

    # fetch row
    Person.get(1)

    # query
    people = Person.select(Person.q.name=='John')

See the `SQLObject documentation`_ for details. Just remember that our database
connection is available as ``orm.db`` where ``orm`` is the extension object.

.. _SQLObject documentation: http://sqlobject.org/SQLObject.html

API reference
-------------
"""
import sqlobject

from tool.plugins import BasePlugin


class SQLObjectExtension(BasePlugin):
    """Adds the ORM feature.

    Required configuration options:

    :param uri:
        a string describing the connection, as follows:
        ``scheme://username:password@hostname:port/database_name``
        (see `declaring a connection`_ in SQLObject documentation).

    .. _declaring a connection: http://sqlobject.org/SQLObject.html#declaring-a-connection
    """
    features = 'orm'

    def make_env(self, uri):
        # XXX check if this still makes sense:
        # http://kassemi.blogspot.com/2006/01/cherrypy-sqlite-and-sqlobject-freaking.html
        # ...and apply the solution here if it does.
        conn = sqlobject.connectionForURI(uri)
        sqlobject.sqlhub.threadConnection = conn
        return {'connection': conn}

    @property
    def db(self):
        """The connection instance, as configured here by
        :class:`tool.application.Application`.
        """
        try:
            return self.env['connection']
        except KeyError:
            raise RuntimeError('Connection to DB is missing.')
