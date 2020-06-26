# -*- coding: utf-8 -*-

#
# TODO
#
# Refactor this module. The environment should be stored in plugin instance.
#

from werkzeug import Response
import wtforms
from tool import app
from tool.routing import url, url_for, redirect_to
from tool.signals import called_on
from tool.ext.templating import as_html
from tool.ext.documents import default_storage
from tool.ext.pagination import Pagination
from tool.ext.breadcrumbs import entitled


#from tool.ext.who import requires_auth
from tool.ext.what import require, is_admin
#from repoze.what.predicates import not_anonymous, in_group

from doqu import Document
import doqu.validators
from doqu.ext.forms import document_form_factory


def env(name):
    "Returns plugin environment variable of given name."
    plugin = app.get_feature('admin')
    return plugin.env[name]

# TODO: use tool.context?
#_registered_models = {}
#_urls_for_models = {}
#_excluded_names = {}
#_ordering = {}
#_list_names = {}
#_search_names = {}
def _get_model(namespace, name):
    if namespace not in env('registered_models'):
        raise NameError('There is no registered namespace "%s"' % namespace)
    try:
        return env('registered_models')[namespace][name]
    except KeyError:
        raise NameError('"%s" is not a registered model in namespace %s.' %
                        (name, namespace))

def _get_excluded_names(model):
    return env('excluded_names')[model] or []

def _get_url_for_object(obj):
    if not obj.pk:
        return
    model = type(obj)
    f = env('urls_for_models')[model]
    try:
        return f(obj) if f else None
    except:  # FIXME here was BuildError from Werkzeug
        return None

#-- VIEWS ------------------------------------------------------------------

@url('/')
@require(is_admin())
@entitled(u'Admin site')
@as_html('admin/index.html')
def index(request):
    return {
        'namespaces': env('registered_models'),
    }

@url('/<string:namespace>/')
@require(is_admin())
@entitled(lambda **kw: kw['namespace'])
@as_html('admin/namespace.html')
def namespace(request, namespace):
    return {
        'namespace': namespace,
        'models': env('registered_models')[namespace],
    }

@url('/<string:namespace>/<string:model_name>/')
@require(is_admin())
@entitled(lambda **kw: _get_model(kw['namespace'], kw['model_name'])
                       .meta.get_label_plural())
@as_html('admin/object_list.html')
def object_list(request, namespace, model_name):
    db = default_storage()
    model = _get_model(namespace, model_name)
    query = model.objects(db)

    if 'q' in request.values:
        value = request.values.get('q')
        # TODO: move defs sanity check elsewhere (admin site function?)
        field_names = env('search_names')[model]
        if not field_names:
            raise ValueError('Cannot search {0} objects: search fields are '
                             'not defined'.format(model.__name__))
        assert isinstance(field_names, (list, tuple))
        # FIXME should be q.where(foo=q).or_where(bar=q)
        # but Docu doesn't support OR at the moment
        if 1 < len(field_names):
            raise NotImplementedError('Multiple search fields are not yet '
                                      'supported in this version.')
        # TODO: pre-convert value?
        query = query.where(**{'{0}__matches_caseless'.format(field_names[0]): value})

    ordering = env('ordering').get(model)
    if 'sort_by' in request.values:
        sort_field = request.values.get('sort_by')
        sort_reverse = bool(request.values.get('sort_reverse', False))
        ordering = dict(ordering, names=[sort_field])
    if ordering:
        query = query.order_by(**ordering)

    #pagin_args =  {'namespace': namespace, 'model_name': model_name}
    #objects, pagination = paginated(query, req, pagin_args)
    page = request.values.get('page', 1)
    per_page = request.values.get('per_page', 20)
    pagination = Pagination(query, per_page, page,
                            'tool.ext.admin.views.object_list',
                            namespace=namespace,
                            model_name=model_name)

    list_names = env('list_names')[model] or ['__unicode__']

    return {
        'namespace': namespace,
        'query': query,
        #'objects': objects,
        'pagination': pagination,
        'list_names': list_names,
        'search_enabled': bool(env('search_names')[model]),
    }

@url('/<string:namespace>/<string:model_name>/<string:pk>')
@url('/<string:namespace>/<string:model_name>/add')
@require(is_admin())
@entitled(lambda **kw: (u'{0} {1}').format(
          u'Editing' if 'pk' in kw else 'Adding',
          _get_model(kw['namespace'], kw['model_name']).meta.get_label()))
@as_html('admin/object_detail.html')
def object_detail(request, namespace, model_name, pk=None):
    db = default_storage()
    model = _get_model(namespace, model_name)
    if pk:
        try:
            obj = db.get(model, pk)
        except doqu.validators.ValidationError:
            # Whoops, the data doesn't fit the schema. Let's try converting.
            obj = db.get(Document, pk)
            obj = obj.convert_to(model)
        creating = False
    else:
        obj = model()
        creating = True

    if not creating and request.form.get('DELETE'):
        # TODO: confirmation screen.
        # List related objects, ask what to do with them (cascade/ignore/..)
        obj.delete()
        return redirect_to('tool.ext.admin.views.object_list', namespace=namespace,
                        model_name=model_name)

    DocumentForm = document_form_factory(model, db)

    if not model.meta.structure:
        for k in obj:
            setattr(DocumentForm, k,
                    wtforms.fields.TextField(k.title().replace('_',' ')))

    form = DocumentForm(request.form, obj)

    for name in _get_excluded_names(model):
        del form[name]

    message = None
    if request.method == 'POST' and form.validate():
        form.populate_obj(obj)

        #assert 0==1, 'DEBUG'
        #if not __debug__:

        obj.save(db)    # storage can be omitted if not creating obj

        # TODO: move this to request.session['messages'] or smth like that
        message = u'%s has been saved.' % obj.__class__.__name__
        #if creating:
        # redirect to the same view but change URL
        # from ".../my_model/add/" to
        # to the editing URL ".../my_model/123/"
        # ...hmm, we *should* redirect even after editing an existing item
        return redirect_to('tool.ext.admin.views.object_detail',
                           namespace=namespace, model_name=model_name,
                           pk=obj.pk)
    obj_url = _get_url_for_object(obj)

    # objects of other models that are known to reference this one
    references = {}
    for model, attrs in model.meta.referenced_by.iteritems():
        for attr in attrs:
            qs = model.objects(db).where(**{attr: obj.pk})
            if qs.count():
                references.setdefault(model, {})[attr] = qs

    return {
        'namespace': namespace,
        'object': obj,
        'object_url': obj_url,
        'form': form,
        'message': message,
        'references': references,
        'other_doc_types': env('registered_models'),
    }
