import os


class App:
    DEBUG = os.getenv('DEBUG') in {'1', 'True'}

    SECRET_KEY = os.getenv('SECRET_KEY')

    # sqlalchemy
    # FIXME: load from config file
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs:cs271828@l-im1.biz.nc2/cs'
    SQLALCHEMY_POOL_SIZE = 60
    SQLALCHEMY_ECHO = os.environ.get('ENABLE_SQLALCHEMY_ECHO') is not None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask profiler
    FLASK_PROFILER = {
        "enabled": False
    }


class XChat:
    # FIXME: load from config file
    KEY = 'X6UVFQWSWZHPJGPRARVTPK49NU1LHEO1HKQZWMM9VQXBOQWGJ99BQ0ADAWCIERGJ'

    WS_URL = 'wss://xchat.qinqinxiaobao.com/ws'


class XChatClient:
    ROOT_URL = "http://l.xchat.com"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] (%(processName)s:%(process)d/%(thread)d) %(name)s: %(message)s'
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
            'level': 'INFO',
            'propagate': False
        },
        'app.utils': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
    },
}
