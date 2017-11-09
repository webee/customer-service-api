from flask import request
from flask_restplus import Resource, abort
from app.service.models import App
from app import jwt
from app.apis.jwt import current_application, require_app
from app.apis.jwt import current_customer, require_customer
from app.apis.jwt import current_staff, require_staff
from .api import api
from .serializers import app_auth_data, customer_auth_data, staff_auth_data, app_change_password_data
from .parsers import uid_args
from app.apis.serializers.auth import token_data
from app.apis.commons.auth import auth_token as _token


@api.route('/app_token')
class AppToken(Resource):
    @api.expect(app_auth_data)
    @api.marshal_with(token_data)
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        """生成app token"""
        return _token('app', request.get_json(), lambda app, data: app)

    @require_app
    @api.marshal_with(token_data)
    def put(self):
        """刷新app token"""
        return dict(token=jwt.encode_token('app', current_application))


@api.route('/change_app_password')
class AppPassword(Resource):
    @api.expect(app_change_password_data)
    @api.marshal_with(token_data)
    @api.response(204, 'password changed')
    @api.response(401, 'change password failed')
    def post(self):
        """修改app密码"""
        data = request.get_json()
        app_name = data['app_name']
        app_password = data['app_password']
        app = App.authenticate(app_name, app_password)

        if app is None:
            abort(401, 'invalid credentials')

        new_password = data['new_password']
        if not app.change_password(app_password, new_password):
            abort(401, 'change password failed')
        return None, 204


@api.route('/customer_token')
class CustomerToken(Resource):
    @api.expect(customer_auth_data)
    @api.marshal_with(token_data)
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        """生成customer token"""
        return _token('customer', request.get_json(), lambda app, data: app.customers.filter_by(uid=data['uid']).one_or_none())

    @require_app
    @api.expect(uid_args)
    @api.marshal_with(token_data)
    def get(self):
        """使用app生成customer token"""
        args = uid_args.parse_args()
        uid = args['uid']
        app = current_application

        return dict(token=jwt.encode_token('customer', app.customers.filter_by(uid=uid).one_or_none()))

    @require_customer
    @api.marshal_with(token_data)
    def put(self):
        """刷新customer token"""
        return dict(token=jwt.encode_token('customer', current_customer))


@api.route('/staff_token')
class StaffToken(Resource):
    @api.expect(staff_auth_data)
    @api.marshal_with(token_data)
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        """生成staff token"""
        return _token('staff', request.get_json(), lambda app, data: app.staffs.filter_by(uid=data['uid']).one_or_none())

    @require_app
    @api.expect(uid_args)
    @api.marshal_with(token_data)
    def get(self):
        """使用app生成staff token"""
        args = uid_args.parse_args()
        uid = args['uid']
        app = current_application

        return dict(token=jwt.encode_token('staff', app.staffs.filter_by(uid=uid).one_or_none()))

    @require_staff
    @api.marshal_with(token_data)
    def put(self):
        """刷新staff token"""
        return dict(token=jwt.encode_token('staff', current_staff))
