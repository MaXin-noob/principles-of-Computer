# -*- coding: utf-8 -*-
"""
Data Analysis
=============

:state: alpha (demo)
:dependencies: Doqu_, Dark_

Web interface for Data Analysis and Reporting Kit (`Dark`_).
Requires :mod:`tool.ext.documents` to be properly set up.

.. _Doqu: http://pypi.python.org/pypi/doqu
.. _Dark: http://pypi.python.org/pypi/dark

.. note::

    Current implementation is very crude. Please refer to the `Dark
    documentation`_ (namely the `shaping` module) for details.

.. _Dark documentation: http://packages.python.org/dark

.. warning::

    Current implementation does not offer any authentication/authorization so
    this module **must** be activated only in a trusted environment. Remember
    that it exposes the whole data storage.

"""
from tool.routing import url, redirect_to
from tool.plugins import BasePlugin
from werkzeug import Response
import wtforms
from tool.ext.templating import as_html, register_templates
from tool.ext.documents import default_storage
from doqu import Document
import dark
from dark.aggregates import *


class DarkPlugin(BasePlugin):
    def make_env(self):
        register_templates(__name__)


# FIXME STUBS!!!!
login_required = lambda f: f


aggregate_classes = (Avg, Count, Max, Median, Min, Sum, Qu1, Qu3)
AGGREGATE_MAP = dict((cls.__name__, cls) for cls in aggregate_classes)
#AGGREGATE_CHOICES = [(k, k) for cls in aggregate_classes]

class CastForm(wtforms.Form):
    factors = wtforms.TextField()
    pivot_factors = wtforms.TextField()
    aggregate_class = wtforms.SelectField(choices=zip(AGGREGATE_MAP, AGGREGATE_MAP))
    aggregate_factor = wtforms.TextField()

    def get_aggregate(self):
        if self.validate():
            cls_name = self.data['aggregate_class']
            factor   = self.data['aggregate_factor']
            if cls_name and factor:
                cls = AGGREGATE_MAP[cls_name]
                return cls(factor)


@url('/')
@login_required
@as_html('analysis/report.html')
def report(request):
    query = Document.objects(default_storage())  # TODO: only docs registered with admin?
    form = CastForm(request.form)
    factors = []
    pivot_factors = []
    aggregate = Count()
    if form.validate():
        factors = form.data.get('factors')
        factors = factors.split(' ') if factors else []
        pivot_factors = form.data.get('pivot_factors')
        pivot_factors = pivot_factors.split(' ') if pivot_factors else []
        aggregate = form.get_aggregate() or Count()
    table = dark.cast(query, factors, pivot_factors, aggregate)
    return {'form': form, 'table': table}

