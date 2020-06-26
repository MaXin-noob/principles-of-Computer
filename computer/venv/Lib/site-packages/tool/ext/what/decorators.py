from functools import wraps
from repoze.what.predicates import NotAuthorizedError
from werkzeug import Response


__all__ = ['require']


def require(predicate):
    """
    Decorates given function and protects it from being executed without
    given permissions. The function is only executed if and only if
    authorization is granted (i.e., the predicate is met).

    This is a simplified version of the `require` decorator from
    repoze.who-pylons. Custom denial handlers are not supported.
    """
    def outer(f):
        @wraps(f)
        def inner(request, *args, **kwargs):
            try:
                predicate.check_authorization(request.environ)
            except NotAuthorizedError as e:
                reason = unicode(e)
                if request.environ.get('repoze.who.identity'):
                    # The user is authenticated.
                    code = 403
                else:
                    # The user is not authenticated.
                    code = 401
                return Response(reason, code)
            else:
                return f(request, *args, **kwargs)
        return inner
    return outer

