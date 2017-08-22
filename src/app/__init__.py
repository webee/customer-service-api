import os

from flask import Flask, jsonify
from pytoolbox.util import pmc_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from app.utils import dbs
from app.entry.utils.jwt import JWT

# extensions
db = SQLAlchemy()
migrate = Migrate(directory=os.path.join(os.path.dirname(__file__), 'migrations'))
bcrypt = Bcrypt()
cors = CORS()
jwt = JWT()


def create_app(env='dev'):
    app = Flask(__name__)
    # app = Flask(__name__)

    # 最先初始化配置
    init_config(app, env)

    init_extensions(app)

    register_mods(app)

    init_errors(app)

    return app


def init_config(app, env):
    from . import config

    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    app.config.from_object(config.App)


def init_extensions(app):
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

    # jwt
    jwt.init_app(app)


def register_mods(app):
    from .entry.auth.entry import entry as auth_entry
    from .entry.main.entry import entry as main_entry
    from .entry.bucket.entry import entry as bucket_entry

    app.register_blueprint(auth_entry, url_prefix='/auth')
    app.register_blueprint(main_entry, url_prefix='/')
    app.register_blueprint(bucket_entry, url_prefix='/buckets')


def init_errors(app):
    from .errors import BizError, biz_error_handler

    app.register_error_handler(BizError, biz_error_handler)

    for code in [404, 500]:
        def handler(_code):
            def h(e):
                return jsonify(ret=False, code=_code, msg=str(e)), _code
            return h
        app.register_error_handler(code, handler(code))

