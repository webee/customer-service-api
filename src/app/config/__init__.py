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
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # jwt
    JWT_AUTH_HEADER_PREFIX = 'JWT'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or '.yek tset'
    JWT_EXPIRATION_DELTA = timedelta(days=2)
    JWT_LEEWAY = timedelta(minutes=10)
    JWT_DEFAULT_ROLE = 'app'
