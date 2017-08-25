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

    api.errorhandler(BizError)(biz_error_handler)

    # init app
    api.init_app(app)
