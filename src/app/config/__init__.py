from pytoolbox.util.pmc_config import get_project_root
import os
from datetime import timedelta

root = get_project_root()


class App:
    SECRET_KEY = os.getenv('SECRET_KEY') or '.yek tset'
    TESTING = False
    DEBUG = True

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs:cs1234@localhost/custom_service'
    SQLALCHEMY_ECHO = not os.environ.get('DISABLE_SQLALCHEMY_ECHO', False)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # jwt
    JWT_AUTH_HEADER_PATTERN = 'X-%s-JWT'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or '.yek tset'
    JWT_EXPIRATION_DELTA = timedelta(days=2)
    JWT_LEEWAY = timedelta(minutes=10)
    JWT_DEFAULT_ROLE = 'app'

    # restplus
    ERROR_404_HELP = False
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    SWAGGER_UI_JSONEDITOR = False


class XChatClient:
    NS = 'cs'
    KEY = 'demo app cs key.'

    ROOT_URL = "http://local.xchat.com"


class XChatKafka:
    BOOTSTRAP_SERVERS = ['localhost:9092', 'localhost:9093', 'localhost:9094']

    CS_MSGS_TOPIC = 'xchat_cs_msgs'
    CONSUMER_GROUP = 'xchat_cs_msgs'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
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
    },
}
