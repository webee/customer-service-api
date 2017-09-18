from flask_restplus import Api
from flask import Blueprint

blueprint = Blueprint('api', __name__)
authorizations = {
    role + '-jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-%s-JWT' % role.upper()
    }
    for role in ['app', 'customer', 'staff']
}
api = Api(blueprint, version='1.0', doc='/',
          title='客服系统API', description='包括后端、App端和客服端',
          authorizations=authorizations)


def init_api():
    # jwt
    from . import jwt

    # add namespaces
    from .namespaces.bucket.api import api as bucket_api
    api.add_namespace(bucket_api, path='/buckets')

    from .namespaces.auth.api import api as auth_api
    api.add_namespace(auth_api, path='/auth')

    from .namespaces.app.api import api as app_api
    api.add_namespace(app_api, path='/app')

    # from .staff.api import api as staff_api
    # api.add_namespace(staff_api, path='/staff')

    # error handlers
    from app.errors import BizError, biz_error_handler
    from sqlalchemy.orm.exc import NoResultFound
    from app.errors import db_not_found_error_handler

    api.errorhandler(BizError)(biz_error_handler)
    api.errorhandler(NoResultFound)(db_not_found_error_handler)
