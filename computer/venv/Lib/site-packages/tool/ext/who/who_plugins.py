__all__ = ['DoquPlugin']


#from tool.ext.documents import storages
from tool.plugins import get_feature
from schema import User


class DoquPlugin(object):
    """ Doqu-powered authenticator and metadata provider for repoze.who.
    """

    def __init__(self):
        pass

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        try:
            username = identity['login']
            password = identity['password']
        except KeyError:
            return None

        db = get_feature('authentication').env['database']

        users = User.objects(db).where(username=username)

        if not users:
            return None

        assert len(users) == 1, ('expected only one user with username {0}, '
                                 'got {1}'.format(username, len(users)))

        user = users[0]

        if user.check_password(password):
            return user.pk

        return None

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        db = get_feature('authentication').env['database']
        userid = identity.get('repoze.who.userid')
        try:
            instance = db.get(User, userid)
        except KeyError:
            pass
        else:
            identity['instance'] = instance
            #identity.update(info)
