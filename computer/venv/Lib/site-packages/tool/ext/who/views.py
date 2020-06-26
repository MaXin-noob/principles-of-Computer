# -*- coding: utf-8 -*-

# XXX there are no real views here; rename the module

from tool.ext.templating import render_template

from forms import LoginForm


def render_login_form(env):
    """
    This is not a proper view: it gets environment (instead of request) and
    returns a string representation of the HTML form (instead of a response
    object).
    """
    request = env['werkzeug.request']
    form = LoginForm(request.form)
    #if request.method == 'POST' and form.validate():
    #    hm.. FormPlugin should have done the job already :)
    result = render_template('login.html', form=form)
    return str(result.encode('utf-8'))
