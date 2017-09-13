from flask import request
from flask_restplus import Resource, abort
from app.service.models import App
from .. import jwt
from ..auth.jwt import current_app_client, require_app
from ..auth.jwt import current_customer, require_customer
from ..auth.jwt import current_staff, require_staff
from .api import api
from .serializers import app_auth_data, customer_auth_data, staff_auth_data, app_change_password_data


def _token(role, data, get_identity_from_app):
    app_name = data['app_name']
    app_password = data['app_password']

    app = App.authenticate(app_name, app_password)

    if app is None:
        abort(401, 'invalid credentials')

    identity = get_identity_from_app(app, data)
    return dict(token=jwt.encode_token(role, identity))


@api.route('/app_token')
class AppToken(Resource):
    @api.expect(app_auth_data)
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        """生成app token"""
        return _token('app', request.get_json(), lambda app, data: app)


@api.route('/refresh_app_token')
class RefreshAppToken(Resource):
    @require_app
    def post(self):
        """刷新app token"""
        return dict(token=jwt.encode_token('app', current_app_client))


@api.route('/change_app_password')
class AppPassword(Resource):
    @api.expect(app_change_password_data)
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
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        """生成customer token"""
        return _token('customer', request.get_json(), lambda app, data: app.customers.filter_by(uid=data['uid']).one_or_none())


@api.route('/refresh_customer_token')
class RefreshCustomerToken(Resource):
    @require_customer
    def post(self):
        """刷新customer token"""
        return dict(token=jwt.encode_token('customer', current_customer))


@api.route('/staff_token')
class StaffToken(Resource):
    @api.expect(staff_auth_data)
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        """生成staff token"""
        return _token('staff', request.get_json(), lambda app, data: app.customers.filter_by(uid=data['uid']).one_or_none())


@api.route('/refresh_staff_token')
class RefreshStaffToken(Resource):
    @require_staff
    def post(self):
        """刷新staff token"""
        return dict(token=jwt.encode_token('staff', current_staff))
