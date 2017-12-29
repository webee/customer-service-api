from collections import OrderedDict
from flask_restplus import fields
from app import ma
from .. import api


def raw_field(f):
    """
    ignore readonly fields
    :param f:
    :return:
    """
    if f.readonly:
        return

    if isinstance(f, fields.List):
        m = raw_field(f.container)
        if m:
            return fields.List(m)
    elif isinstance(f, fields.Nested):
        m = raw_model(f.model)
        if m:
            return fields.Nested(m)
    else:
        return f


def raw_model(model):
    """
    remove readonly fields
    :param model: complete model
    :return: raw model without readonly fields
    """
    raw_name = 'Raw %s' % model.name
    if raw_name in api.models:
        return api.models[raw_name]

    parents = []
    for p in model.__parents__:
        m = raw_model(p)
        if m:
            parents.append(m)

    raw_specs = OrderedDict()
    for n, f in model.items():
        rf = raw_field(f)
        if rf:
            raw_specs[n] = rf

    if len(parents) > 0:
        parents.append(raw_specs)
        return api.model(raw_name, *parents)
    else:
        if len(raw_specs):
            return api.model(raw_name, raw_specs)


def raw_specs(specs):
    res = {}
    for n, f in specs.items():
        rf = raw_field(f)
        if rf:
            res[n] = rf
    return res


# 分页结果
pagination = api.model('A Page of Results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

# 资源id
resource_id = api.model('Resource ID', {
    'id': fields.Integer(readonly=True, description='resource id')
})

# 资源基本信息id, created, updated
base_resource = api.inherit('Resource Base', resource_id, {
    'created': fields.DateTime(readonly=True, descrption='created time'),
    'updated': fields.DateTime(readonly=True, description='updated time')
})


# schemas
class PaginationSchema(ma.Schema):
    page = ma.Integer()
    pages = ma.Integer()
    per_page = ma.Integer()
    total = ma.Integer()


pagination_schema = PaginationSchema()
