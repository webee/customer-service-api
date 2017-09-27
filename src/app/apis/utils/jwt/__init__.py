from functools import wraps
from flask import request, _request_ctx_stack
from flask_restplus import abort
from datetime import datetime, timedelta
import jwt
from werkzeug.local import LocalProxy
from hashlib import md5
import logging

logger = logging.getLogger(__name__)

current_identity = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_identity', None))


CONFIG_DEFAULTS = {
    'JWT_ALGORITHM': 'HS256',
    'JWT_LEEWAY': timedelta(minutes=10),
    'JWT_AUTH_HEADER_PATTERN': 'X-%s-JWT',
    'JWT_EXPIRATION_DELTA': timedelta(days=2),
    'JWT_DEFAULT_ROLE': 'app'
}


class JWT(object):
    def __init__(self, app=None, identity_handler=None, payload_handler=None, identity_secret_handler=None,
                 auth_required_hook=None):
        self.app = app
        self.identity_handler = identity_handler
        self.payload_handler = payload_handler
        self.identity_secret_handler = identity_secret_handler
        self.auth_required_hook = auth_required_hook
        if app is not None:
            self.init_app(app)

        self.current_identity = current_identity

    def as_identity_handler(self, f):
        self.identity_handler = f

    def as_payload_handler(self, f):
        self.payload_handler = f

    def as_identity_secret_handler(self, f):
        self.identity_secret_handler = f

    def as_auth_required_hook(self, f):
        self.auth_required_hook = f

    def init_app(self, app):
        self.app = app
        for k, v in CONFIG_DEFAULTS.items():
            app.config.setdefault(k, v)
        app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])

        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}

        app.extensions['jwt'] = self

    def encode_token(self, role, identity):
        if not identity:
            abort(403, '%s role not found' % role)

        payload = self.payload_handler(role, identity)
        secret = self.app.config['JWT_SECRET_KEY']
        # append sign
        payload['_s'] = self._gen_sign(role, identity)
        algorithm = self.app.config['JWT_ALGORITHM']

        iat = datetime.utcnow()
        exp = iat + self.app.config.get('JWT_EXPIRATION_DELTA')

        payload = dict(exp=exp, iat=iat, role=role, **payload)

        return jwt.encode(payload, secret, algorithm=algorithm).decode('utf-8')

    def _gen_sign(self, role, identity):
        id_secret = self.identity_secret_handler(role, identity) or self.app.config['JWT_SECRET_KEY']
        return md5(id_secret.encode('utf-8')).hexdigest()[:7]

    def auth_required(self, role=None):
        def wrapper(fn):
            fn = self.auth_required_hook(role, fn)

            @wraps(fn)
            def decorator(*args, **kwargs):
                self._auth_required(role)
                return fn(*args, **kwargs)
            return decorator
        return wrapper

    def _auth_required(self, role=None):
        role = role or self.app.config['JWT_DEFAULT_ROLE']
        token = self._get_request_token(role)

        payload = {}
        try:
            payload = self._decode_token(token)
        except jwt.InvalidTokenError as e:
            abort(401, 'invalid token', details=str(e))

        if payload.get('role') != role:
            abort(401, 'invalid token', details='%s role required' % role)

        identity = self.identity_handler(role, payload)

        if identity is None:
            abort(401, '%s role does not exist' % role)

        # check sign
        _s = payload.get('_s')
        if _s != self._gen_sign(role, identity):
            abort(401, 'token is invalid')

        _request_ctx_stack.top.current_identity = identity

    def _get_request_token(self, role):
        jwt_header_pattern = self.app.config['JWT_AUTH_HEADER_PATTERN']
        auth_header_value = request.headers.get(jwt_header_pattern % role.upper(), None)
        if not auth_header_value:
            jwt_header = self.app.config['JWT_AUTH_HEADER']
            auth_header_value = request.headers.get(jwt_header, None)
        if not auth_header_value:
            auth_header_value = request.args.get('_jwt', None)

        if not auth_header_value:
            abort(401, '%s jwt header missing' % role)

        return auth_header_value

    def _decode_token(self, token):
        secret = self.app.config['JWT_SECRET_KEY']
        algorithm = self.app.config['JWT_ALGORITHM']
        leeway = self.app.config['JWT_LEEWAY']

        verify_claims = ['signature', 'exp', 'iat']

        options = {
            'verify_' + claim: True
            for claim in verify_claims
        }

        return jwt.decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)
