import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.apis import api
from app.apis.utils.jwt import JWT
from app.utils import dbs
from pytoolbox.util import pmc_config

# extensions
jwt = JWT()

db = SQLAlchemy()
migrate = Migrate(directory=os.path.join(os.path.dirname(__file__), 'migrations'))
bcrypt = Bcrypt()
cors = CORS()


def create_app(env='dev'):
    app = Flask(__name__)
    # 最先初始化配置
    init_config(app, env)

    register_mods(app)
    init_extensions(app)
    init_errors(app)

    return app


def init_config(app, env):
    from . import config

    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    app.config.from_object(config.App)


def register_mods(app):
    pass


def init_extensions(app):
    # jwt
    jwt.init_app(app)
    jwt.auth_required_hook = lambda role, func: api.doc(security=role + '-jwt')(func)

    # api
    from .apis import init_api
    init_api(app)

    # db
    from .service import test_models
    from .service import models

    db.init_app(app)
    dbs.init_app(app)
    migrate.init_app(app, db)

    # bcrypt
    bcrypt.init_app(app)

    # cors
    cors.init_app(app)


def init_errors(app):
    pass
