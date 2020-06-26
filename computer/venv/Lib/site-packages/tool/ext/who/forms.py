# -*- coding: utf-8 -*-

from wtforms import Form, TextField, PasswordField, validators
from wtforms.validators import length, required


class LoginForm(Form):
    username = TextField(u'User name', validators=[
        required(),
        length(min=2, max=16),
    ])
    password = PasswordField(u'Password', validators=[
        required(),
        length(min=6, max=16),
    ])
