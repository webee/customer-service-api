import jwt
from datetime import datetime
from functools import wraps
from flask import request, _request_ctx_stack
from werkzeug.local import LocalProxy
from app.config import test_app as config
from app.utils.app_client.constant import ErrorCode
from .api import api
from . import resp

current_appid = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_appid', None))


def auth_required(fn):
    fn = api.doc(security=['test-app-appid', 'test-app-token'])(fn)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        appid = request.headers.get('X-App-Id') or request.args.get('appid')
        token = request.headers.get('X-Token') or request.args.get('token')
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return resp.fail(ErrorCode.TOKEN_EXPIRED, 'token过期')
        except jwt.InvalidTokenError:
            return resp.fail(ErrorCode.INVALID_TOKEN, 'token非法')

        if appid != payload.get('appid'):
            return resp.fail(ErrorCode.INVALID_TOKEN, 'token非法')

        _request_ctx_stack.top.current_appid = appid

        return fn(*args, **kwargs)

    return wrapper


def decode_token(token):
    secret = config.JWT_SECRET_KEY
    algorithm = config.JWT_ALGORITHM

    verify_claims = ['signature', 'exp', 'iat']

    options = {
        'verify_' + claim: True
        for claim in verify_claims
    }

    return jwt.decode(token, secret, options=options, algorithms=[algorithm])


def encode_token():
    appid = request.args.get('appid') or request.headers.get('X-App-Id')
    appkey = request.args.get('appkey') or request.headers.get('X-App-Key')
    if not (appid == config.APPID and appkey == config.APPKEY):
        raise Exception('auth failed')

    secret = config.JWT_SECRET_KEY
    algorithm = config.JWT_ALGORITHM
    iat = datetime.utcnow()
    exp = iat + config.JWT_EXPIRATION_DELTA
    payload = dict(appid=appid, exp=exp, iat=iat)

    return dict(token=jwt.encode(payload, secret, algorithm=algorithm).decode('utf-8'), exp=exp.timestamp())
