# -*- coding: utf-8 -*-

from tool import app


__all__ = ['get_user']


def get_user(request=None):
    """
    Returns a :class:`~tool.ext.who.User` instance associated with
    current user. If the user is not logged in, returns `None`.

    This information is available through any request object but buried deep
    inside of it. The document instance is provided by
    :class:`~tool.ext.who.plugins.DocuPlugin`. Make sure it is loaded if
    you are using a custom configuration instead of presets.

    Usage::

        def some_view(request):
            user = get_user(request)

    The request object is optional::

        user = get_user()

    If you only need the `User` document's primary key, there's a more
    straightforward way::

        def some_view(request):
            user_id = request.remote_user

    """
    request = request or app.request
    try:
        return request.environ['repoze.who.identity']['instance']
    except KeyError:
        return None
