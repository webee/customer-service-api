import os

from flask import Flask, jsonify
from flask_api import FlaskAPI
from pytoolbox.util import pmc_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.utils import dbs

# extensions
db = SQLAlchemy()
migrate = Migrate(directory=os.path.join(os.path.dirname(__file__), 'migrations'))


def create_app(env='dev'):
    app = FlaskAPI(__name__)

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


def register_mods(app):
    from .entry.main.entry import entry as main_entry
    from .entry.bucket.entry import entry as bucket_entry

    app.register_blueprint(main_entry, url_prefix='/')
    app.register_blueprint(bucket_entry, url_prefix='/buckets')


def init_errors(app):
    for code in [404, 500]:
        def handler(_code):
            def h(e):
                return jsonify(ret=False, code=_code, msg=str(e)), _code
            return h
        app.register_error_handler(code, handler(code))

