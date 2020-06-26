# -*- coding: utf-8 -*-

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from werkzeug import generate_password_hash, check_password_hash
from doqu import Document, validators
from doqu.ext.fields import Field
# FIXME: commented out to avoid circular import; reorganize the code there
#from tool.ext.admin import with_admin


#@with_admin(namespace='auth')
class User(Document):
    """
    Represents a user. You can extend this class in whatever way you need, just
    keep in mind that :meth:`User.set_password` and :meth:`User.check_password`
    are essential for correct authentication.
    """
    username = Field(unicode, required=True)
    password = Field(unicode, required=True)
    is_admin = Field(bool, default=False)

    validators = {
        'username': [validators.Length(min=2, max=16)],
    }

    def __unicode__(self):
        return u'{username}'.format(**self)

    def set_password(self, raw_password):
        self.password = unicode(generate_password_hash(raw_password))

    def check_password(self, raw_password):
        assert self.password and '$' in self.password, 'bad stored password'
        return check_password_hash(self.password, raw_password)
