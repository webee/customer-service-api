from flask import request
from flask_restplus import Resource, abort
from app.service.models import App
from app import jwt
from app.utils.jwt import current_app_client, require_app
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
        return _token('app', request.get_json(), lambda app, data: app)


@api.route('/change_app_password')
class AppPassword(Resource):
    @require_app
    @api.expect(app_change_password_data)
    @api.response(204, 'password changed')
    @api.response(401, 'change password failed')
    def post(self):
        app = current_app_client
        data = request.get_json()

        if not app.change_password(data['password'], data['new_password']):
            abort(401, 'change password failed')
        return None, 204


@api.route('/customer_token')
class CustomerToken(Resource):
    @api.expect(customer_auth_data)
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        return _token('customer', request.get_json(), lambda app, data: app.customers.filter_by(uid=data['uid']).one_or_none())


@api.route('/staff_token')
class StaffToken(Resource):
    @api.expect(staff_auth_data)
    @api.response(401, 'invalid credentials')
    @api.response(200, 'token successfully generated')
    def post(self):
        return _token('staff', request.get_json(), lambda app, data: app.customers.filter_by(uid=data['uid']).one_or_none())
