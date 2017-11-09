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


class Biz:
    CLOSED_SESSION_ALIVE_TIME = timedelta(hours=24)
