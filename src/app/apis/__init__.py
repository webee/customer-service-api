import logging
from flask_restplus import Api
from flask import Blueprint
from app.errors import BizError, biz_error_handler
from sqlalchemy.orm.exc import NoResultFound
from app.errors import db_not_found_error_handler

logger = logging.getLogger(__name__)

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
          title='客服系统API', description='包括应用后端、客户端和客服端',
          authorizations=authorizations)


# error handlers
api.errorhandler(BizError)(biz_error_handler)
api.errorhandler(NoResultFound)(db_not_found_error_handler)


def init_api(app):
    # jwt
    from . import jwt

    # add namespaces
    if app.debug:
        from .namespaces.bucket.api import api as bucket_api
        api.add_namespace(bucket_api, path='/buckets')

        from .namespaces.test.api import api as test_api
        api.add_namespace(test_api, path='/test')

    from .namespaces.auth.api import api as auth_api
    api.add_namespace(auth_api, path='/auth')

    from .namespaces.app.api import api as app_api
    api.add_namespace(app_api, path='/app')

    from .namespaces.staff.api import api as staff_api
    api.add_namespace(staff_api, path='/staff')

    from .namespaces.customer.api import api as customer_api
    api.add_namespace(customer_api, path='/customer')

    from .namespaces.xchat.api import api as xchat_api
    api.add_namespace(xchat_api, path='/xchat')
