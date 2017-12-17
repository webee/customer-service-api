from app.service.models import App
from flask_restplus import abort
from app import jwt


def auth_token(role, data, get_identity_from_app):
    app_name = data['app_name']
    app_password = data['app_password']

    app = App.authenticate(app_name, app_password)

    if app is None:
        abort(401, 'invalid credentials')

    identity = get_identity_from_app(app, data)
    return jwt.encode_token(role, identity)
