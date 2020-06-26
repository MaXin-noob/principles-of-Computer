# -*- coding: utf-8 -*-
"""
Extensions
==========

.. warning::

    This document is out of date. See :doc:`plugins` API.

Tool is a general purpose framework. It does not impose a certain stack of
technologies related to data storage, templating and so on. Still, Tool has
some batteries included. The glue code comes in "bundles" (Python modules with
optional setup functions). When you need to activate a certain extension, just
include its name or dotted path in the configuration like this (a YAML
example)::

    extensions:
        tool.ext.documents.Documents: nil
        tool.ext.templating.Jinja:
            searchpaths: ['templates/']
        myapp.tool_bundles.foo.Foo: nil

Below is the full list of extensions bundled with Tool.

Database-related
----------------

.. toctree::
   :maxdepth: 1

   ext_documents
   ext_sqlobject
   ext_storm

Web-related
-----------

.. toctree::
   :maxdepth: 1

   ext_admin
   ext_analysis
   ext_http
   ext_pagination
   ext_templating
   ext_who
   ext_what
   ext_werkzeug_routing

Miscellaneous
-------------

.. toctree::
   :maxdepth: 1

   ext_strings

Dependencies
------------

.. note::

    Most extensions depend on external libraries. For example,
    `tool.ext.templating` requires that a certain version of Jinja2 is
    installed. Everything within `tool.ext.*` is considered optional, so only
    basic requirements are installed by default.

    When you try to load an extension, it checks its *own* dependencies via
    `pkg_resources`. The latter peeks into the options `extras_require` and
    `endpoints` defined in Tool's setup.py. If an external package is required
    but not available, or a wrong version is installed, the module
    `pkg_resources` will raise an exception (for example, DistributionNotFound
    or VersionConflict) with a sensible message.

"""
# this is a namespace package
__import__('pkg_resources').declare_namespace(__name__) #pragma NO COVERAGE
