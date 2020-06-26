from tool.ext.who import User
from doqu import Document, Many
from doqu.ext.fields import Field


class Group(Document):
    summary = Field(unicode, required=True)
    is_auth_group = Field(bool, choices=[True], required=True, default=True)

    def __unicode__(self):
        return u'{summary}'.format(**self)

class Member(User):
    groups = Field(Many(Group), essential=True)

