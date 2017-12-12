import jwt
from datetime import datetime
from app import config


def encode_token():
    algorithm = config.XFiles.JWT_ALGORITHM
    secret = config.XFiles.JWT_KEY

    iat = datetime.utcnow()
    exp = iat + config.XFiles.JWT_EXPIRATION_DELTA

    payload = dict(exp=exp, iat=iat, iss=config.App.NAME)

    return jwt.encode(payload, secret, algorithm=algorithm).decode('utf-8')
