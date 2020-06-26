# -*- coding: utf-8 -*-

# python
from functools import wraps

from werkzeug import Response


__all__ = ['requires_auth']


def requires_auth(view):
    """
    Decorator. Ensures that given view is only accessible bu authenticated
    users. If user is not authenticated, (s)he is asked for credentials
    according to the configuration (e.g. using one of presets).
    """
    @wraps(view)
    def inner(request, *args, **kwargs):
        identity = request.environ.get('repoze.who.identity')
        if identity:
            return view(request, *args, **kwargs)
        else:
            return Response(status=401)
    return inner
