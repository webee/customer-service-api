import os
from datetime import timedelta


class App:
    DEBUG = False

    SECRET_KEY = os.getenv('SECRET_KEY')

    # sqlalchemy
    # FIXME: load from config file
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs:cs1234@localhost/custom_service'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # flask profiler
    FLASK_PROFILER = {
        "enabled": False
    }


class XChat:
    # TODO:
    # KEY = 'demo app cs key.'

    WS_URL = 'wss://xchat.qinqinxiaobao.com/ws'


class XChatClient:
    ROOT_URL = "http://l-xchat.com"
