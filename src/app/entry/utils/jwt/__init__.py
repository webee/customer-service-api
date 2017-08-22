from functools import wraps
from flask import request, _request_ctx_stack
from datetime import datetime, timedelta
from app.errors import UnauthorizedError
import jwt
from werkzeug.local import LocalProxy
import logging

logger = logging.getLogger(__name__)

current_identity = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_identity', None))


CONFIG_DEFAULTS = {
    'JWT_ALGORITHM': 'HS256',
    'JWT_LEEWAY': timedelta(minutes=10),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_EXPIRATION_DELTA': timedelta(days=2),
    'JWT_DEFAULT_ROLE': 'app'
}


class JWT(object):
    def __init__(self, app=None, identity_handler=None, payload_handler=None):
        self.app = app
        self.identity_handler = identity_handler
        self.payload_handler = payload_handler
        if app is not None:
            self.init_app(app)

        self.current_identity = current_identity

    def as_identity_handler(self, f):
        self.identity_handler = f

    def as_payload_handler(self, f):
        self.payload_handler = f

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
            raise UnauthorizedError(details='% role not found' % role)

        payload = self.payload_handler(role, identity)
        secret = self.app.config['JWT_SECRET_KEY']
        algorithm = self.app.config['JWT_ALGORITHM']

        iat = datetime.utcnow()
        exp = iat + self.app.config.get('JWT_EXPIRATION_DELTA')

        payload = dict(exp=exp, iat=iat, role=role, **payload)

        return jwt.encode(payload, secret, algorithm=algorithm).decode('utf-8')

    def auth_required(self, role=None):
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                self._auth_required(role)
                return fn(*args, **kwargs)
            return decorator
        return wrapper

    def _auth_required(self, role=None):
        token = self._get_request_token()

        try:
            payload = self._decode_token(token)
        except jwt.InvalidTokenError as e:
            raise UnauthorizedError('Invalid token', str(e))

        role = role or self.app.config['JWT_DEFAULT_ROLE']
        if payload.get('role') != role:
            raise UnauthorizedError('Invalid token', '%s role required' % role)

        _request_ctx_stack.top.current_identity = identity = self.identity_handler(role, payload)

        if identity is None:
            raise UnauthorizedError('Invalid JWT', '%s role does not exist' % role)

    def _get_request_token(self):
        auth_header_value = request.headers.get('Authorization', None)
        auth_header_prefix = self.app.config['JWT_AUTH_HEADER_PREFIX']

        if not auth_header_value:
            raise UnauthorizedError('Invalid JWT header', 'Token missing')

        parts = auth_header_value.split()

        if parts[0].lower() != auth_header_prefix.lower():
            raise UnauthorizedError('Invalid JWT header', 'Unsupported authorization type')
        elif len(parts) == 1:
            raise UnauthorizedError('Invalid JWT header', 'Token missing')
        elif len(parts) > 2:
            raise UnauthorizedError('Invalid JWT header', 'Token contains spaces')

        return parts[1]

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
