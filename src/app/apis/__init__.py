from collections import OrderedDict
from flask_restplus import fields
from flask_restplus import Api


authorizations = {
    role + '-jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-%s-JWT' % role.upper()
    }
    for role in ['app', 'customer', 'staff']
}
api = Api(version='1.0', doc='/', title='客服系统API', description='包括后端、App端和客服端', authorizations=authorizations)


def init_api(app):
    # add namespaces
    from .bucket.api import api as bucket_api
    from .auth.api import api as auth_api
    from .app.api import api as app_api

    api.add_namespace(bucket_api, path='/buckets')
    api.add_namespace(auth_api, path='/auth')
    api.add_namespace(app_api, path='/app')

    # error handlers
    from app.errors import BizError, biz_error_handler
    from sqlalchemy.orm.exc import NoResultFound
    from app.errors import db_not_found_error_handler

    api.errorhandler(BizError)(biz_error_handler)
    api.errorhandler(NoResultFound)(db_not_found_error_handler)

    # init app
    api.init_app(app)


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

    def raw_field(f):
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
        return f

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
