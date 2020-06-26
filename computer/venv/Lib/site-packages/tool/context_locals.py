# -*- coding: utf-8 -*-
"""
Context locals
==============

Contains things you want to have in every single view or helper function or
whatever. Thread safe.

Exports these variables:

* `local` — thread-safe storage object
* `app` — current application object proxy (may not be present)
* `request` — current request object proxy (may not be present)

.. note::

    You should use this module as less as possible. Global data is easy to use
    but hard to debug.

"""
from werkzeug import Local, LocalManager, LocalProxy

__all__ = ['local', 'app', 'request']

local = Local()
local_manager = LocalManager([local])

app = LocalProxy(local, 'app_manager')
request = LocalProxy(local, 'request')
