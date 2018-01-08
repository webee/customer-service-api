from pytoolbox.util.pmc_config import get_project_root
import os
from datetime import timedelta

root = get_project_root()


class App:
    NAME = 'cs'

    TESTING = False
    DEBUG = True

    SECRET_KEY = os.getenv('SECRET_KEY') or '.yek tset'

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs_dev:cs1234@localhost/cs_dev'
    SQLALCHEMY_ECHO = not (os.environ.get('DISABLE_SQLALCHEMY_ECHO', False) or os.environ.get('CELERY_RUNNING', False))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # cache
    CACHE = {
        'CACHE_TYPE': 'redis',
        'CACHE_KEY_PREFIX': NAME + '_',
        'CACHE_REDIS_URL': 'redis://127.0.0.1:6379/13'
    }

    # jwt
    JWT_AUTH_HEADER = 'X-ANY-JWT'
    JWT_AUTH_HEADER_PATTERN = 'X-%s-JWT'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or '.yek tset'
    JWT_EXPIRATION_DELTA = timedelta(days=2)
    JWT_LEEWAY = timedelta(minutes=10)
    JWT_DEFAULT_ROLE = 'app'

    # restplus
    ERROR_404_HELP = False
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    # json.dumps参数
    RESTPLUS_JSON = {}
    SWAGGER_UI_JSONEDITOR = False

    # flask profiler
    FLASK_PROFILER = {
        "enabled": False,
        "storage": {
            "engine": "sqlite",
            "FILE": "flask_profiler.sqlite"
        },
        "ignore": [
            "^((?!\/api\/.+).)*$"
        ]
    }


class Biz:
    CLOSED_SESSION_ALIVE_TIME = timedelta(minutes=5)

    USER_ONLINE_DELTA = timedelta(minutes=3)
    USER_OFFLINE_DELTA = timedelta(seconds=3)


class XChat:
    KEY = 'demo app cs key.'
    DEFAULT_JWT_EXP_DELTA = timedelta(days=30)
    WS_URL = 'ws://local.xchat.com/ws'


class XChatClient:
    ROOT_URL = "http://local.xchat.com"


class XFiles:
    JWT_KEY = "xfiles@qqxb@2017"
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = timedelta(days=2)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] (%(process)d/%(thread)d) %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'app.apis': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'app.utils': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    },
}
