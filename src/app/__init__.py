import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .apis.utils.jwt import JWT

from app.utils import dbs
from pytoolbox.util import pmc_config
from .utils.xchat_client import XChatClient
from .task.xchat import XChatMsgsConsumer

# extensions
jwt = JWT()
db = SQLAlchemy()
migrate = Migrate(directory=os.path.join(os.path.dirname(__file__), 'migrations'))
bcrypt = Bcrypt()
cors = CORS()

xchat_client = XChatClient()
xchat_msgs_consumer = XChatMsgsConsumer()


def create_app(env='dev'):
    app = Flask(__name__)
    # 最先初始化配置
    init_config(app, env)

    init_extensions(app)
    init_errors(app)
    register_mods(app)

    return app


def init_config(app, env):
    from logging.config import dictConfig
    from . import config

    os.environ['ENV'] = env
    pmc_config.register_config(config, env=env)

    dictConfig(config.LOGGING)
    app.config.from_object(config.App)


def register_mods(app):
    from .apis import init_api, blueprint as api

    init_api()
    app.register_blueprint(api, url_prefix='/api')


def init_extensions(app):
    # jwt
    jwt.init_app(app)

    # db
    from .service import test_models
    from .service import models

    db.init_app(app)
    dbs.init_app(app, db)
    migrate.init_app(app, db)

    # bcrypt
    bcrypt.init_app(app)

    # cors
    cors.init_app(app)

    # xchat client
    from . import config
    xchat_client.init_config(config.XChatClient)

    # xchat msgs consumer
    xchat_msgs_consumer.init_app(app, config.XChatKafka)


def init_errors(app):
    pass
