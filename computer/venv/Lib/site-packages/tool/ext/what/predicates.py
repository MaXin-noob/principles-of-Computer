from repoze.what.predicates import *

class is_admin(Predicate):
    """
    Ensures that given account has the `is_admin` flag set.
    Asserts that :doc:`ext_who` is configured correctly.

    To get this work you need to have at least one admin user::

        $ ./manage.py shell
        >>> from tool.ext.who import User
        >>> user = User.objects(db)[0]   # make sure it's you ;-)
        >>> user.is_admin = True
        >>> user.save()

    Okay, that's enough to let you in through the protected views.
    """
    message = 'The current user must be admin'
    def evaluate(self, environ, credentials):
        try:
            user = environ['repoze.who.identity']['instance']
        except KeyError:
            self.unmet('Could not identify user: environ not ready?')
        if not user.is_admin:
            # Raise an exception because the predicate is not met.
            self.unmet()

