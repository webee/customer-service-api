import os
from werkzeug.contrib.profiler import ProfilerMiddleware
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_profiler import Profiler
from .apis.utils.jwt import JWT

from app.utils import dbs
from pytoolbox.util import pmc_config
from .utils.xchat_client import XChatClient

# extensions
profiler = Profiler()
jwt = JWT()
db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate(directory=os.path.join(os.path.dirname(__file__), 'migrations'))
bcrypt = Bcrypt()
cors = CORS()

xchat_client = XChatClient()


def create_app(env='dev'):
    app = Flask(__name__)
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
    # jwt
    jwt.init_app(app)

    # db
    if app.debug:
        from .service import test_models
    from .service import models

    db.init_app(app)
    dbs.init_app(app, db)
    migrate.init_app(app, db)

    ma.init_app(app)

    # bcrypt
    bcrypt.init_app(app)

    # cors
    cors.init_app(app)

    # xchat client
    from . import config
    xchat_client.init_config(config.App.NAME, config.XChat.KEY, config.XChatClient)


def init_errors(app):
    pass
