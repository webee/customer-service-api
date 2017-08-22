from flask import request
from app.utils.api import require_data, current_data
from app.utils import resp
from app import jwt
from .entry import entry as mod
from .schemas import new_app_token_schema, new_customer_token_schema, new_staff_token_schema
from app.service.models import App
from app.errors import UnauthorizedError


def _token(role, get_identity_from_app):
    data = current_data
    app_name = data['app_name']
    app_password = data['app_password']

    app = App.authenticate(app_name, app_password)

    if app is None:
        raise UnauthorizedError(details='Invalid credentials')

    identity = get_identity_from_app(app, data)
    return resp.success(token=jwt.encode_token(role, identity))


@mod.route('/app_token', methods=['POST'])
@require_data(new_app_token_schema)
def app_token():
    return _token('app', lambda app, data: app)


@mod.route('/customer_token', methods=['POST'])
@require_data(new_customer_token_schema)
def customer_token():
    return _token('customer', lambda app, data: app.customers.filter_by(uid=data['uid']).one_or_none())


@mod.route('/staff_token', methods=['POST'])
@require_data(new_staff_token_schema)
def staff_token():
    return _token('staff', lambda app, data: app.staffs.filter_by(uid=data['uid']).one_or_none())


@mod.route('/change_password')
def change_password():
    data = request.get_json()
