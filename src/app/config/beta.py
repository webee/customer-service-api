import os


class App:
    NAME = 'cs'

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs_dev:cs1234@localhost/cs_beta'
    SQLALCHEMY_ECHO = os.environ.get('ENABLE_SQLALCHEMY_ECHO') is not None

    # cache
    CACHE = {
        'CACHE_TYPE': 'redis',
        'CACHE_KEY_PREFIX': NAME + '_',
        'CACHE_REDIS_URL': 'redis://127.0.0.1:6379/15'
    }


class XChat:
    WS_URL = 'ws://b.xchat.qinqinxiaobao.com/ws'


class XChatClient:
    ROOT_URL = "http://l-b.xchat.com"
