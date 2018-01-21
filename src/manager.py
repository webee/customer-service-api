import logging
from flask_script import Manager, Shell, Server
from app import db, create_app
from commands import Celery

logger = logging.getLogger(__name__)

manager = Manager(create_app)
manager.add_option('-e', '--env', dest='env', default='dev', required=False)

manager.add_command('celery', Celery('app.task:app'))


def make_shell_context():
    import app
    from app import config

    return dict(manager=manager, flask_app=manager.app, config=config, app=app, db=db)


manager.add_command("shell", Shell(make_context=make_shell_context))

server = Server(host="0.0.0.0", port=5000)
manager.add_command("runserver", server)


@manager.option('-d', '--drop_all', action="store_true", dest="drop_all", required=False, default=False)
def init_db(drop_all):
    from app import db
    from app.data import init_data

    if drop_all:
        db.drop_all()
    db.create_all()

    # init data
    init_data()


@manager.option('proj_ids', nargs='*', type=int, help='project id')
def sync_proj_msgs(proj_ids):
    from app.task import tasks

    for proj_id in proj_ids:
        logging.info('sync: %d', proj_id)
        tasks.try_sync_proj_xchat_msgs.delay(proj_id=proj_id)


@manager.option('-a', '--app_name', type=str, dest="app_name", required=True, help='app name')
@manager.option('-b', '--batch_size', type=int, dest="batch_size", required=False, default=100, help='batch size')
def create_projects(app_name, batch_size):
    import sys
    import json
    from app.service.models import App
    from app.biz import app as app_biz

    app = App.query.filter_by(name=app_name).one()

    data = [json.loads(line) for line in sys.stdin.readlines()]

    app_biz.batch_create_projects(app, data, batch_size=batch_size)


if __name__ == '__main__':
    manager.run()
