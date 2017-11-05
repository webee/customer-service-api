import os
from datetime import timedelta


class App:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False

    # sqlalchemy
    # FIXME: load from config file
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs:cs1234@localhost/custom_service'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Biz:
    CLOSED_SESSION_ALIVE_TIME = timedelta(hours=6)
