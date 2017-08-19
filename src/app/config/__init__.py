from pytoolbox.util.pmc_config import get_project_root
import os

root = get_project_root()


class App:
    SECRET_KEY = os.getenv('SECRET_KEY') or '.yek tset'
    TESTING = False
    DEBUG = True

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs:cs1234@localhost/custom_service'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
