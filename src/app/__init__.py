import os
# from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from flask_profiler import Profiler
from .apis.utils.jwt import JWT

from app.utils import dbs
from pytoolbox.util import pmc_config
from .utils.xchat_client import XChatClient
from .utils.app_client import AppClients

# extensions
profiler = Profiler()
jwt = JWT()
db = SQLAlchemy()
cache = Cache()
ma = Marshmallow()
bcrypt = Bcrypt()
cors = CORS()

xchat_client = XChatClient()
app_clients = AppClients()


def create_app(env='dev'):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    # if env == 'dev':
    #     app.wsgi_app = ProfilerMiddleware(app.wsgi_app)
    # 最先初始化配置
    init_config(app, env)

    # tasks
    init_tasks(app)

    init_extensions(app)
    init_errors(app)
    register_mods(app)

    # profiler
    # if env == 'dev':
    #     profiler.init_app(app)

    return app


def init_config(app, env):
    from logging.config import dictConfig
    from . import config

    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)
    pmc_config.register_config(config, 'test_app', env=env)
    pmc_config.register_config(config, 'celery_task', env=env, require_upper=False)

    dictConfig(config.LOGGING)
    app.config.from_object(config.App)


def init_tasks(app):
    from app.task import app as celery_app
    from app.task import init_celery_app
    from app.config import celery_task as celery_config

    init_celery_app(celery_app, celery_config, app)


def register_mods(app):
    from .apis import init_api, blueprint as api

    init_api(app)
    app.register_blueprint(api, url_prefix='/api')


def init_extensions(app):
    from . import config

    # jwt
    jwt.init_app(app)

    # db
    if app.debug:
        from .service import test_models
    from .service import models

    db.init_app(app)
    dbs.init_app(app, db)

    # cache
    cache.init_app(app, config=config.App.CACHE)

    ma.init_app(app)

    # bcrypt
    bcrypt.init_app(app)

    # cors
    cors.init_app(app)

    # app clients
    app_clients.init_app(app, cache)

    # xchat client
    xchat_client.init_config(config.App.NAME, config.XChat.KEY, config.XChatClient)


def init_errors(app):
    pass
