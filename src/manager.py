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


def _migrate_proj_msgs(proj, msgs, start_msg_id=1, batch_size=200):
    from app.utils.commons import batch_split
    from app import xchat_client
    from app.task import tasks

    xchat = proj.xchat
    if xchat.start_msg_id < start_msg_id:
        return

    count = 0
    for split_msgs in batch_split(msgs, batch_size):
        _, n = xchat_client.insert_chat_msgs(xchat.chat_id, split_msgs, start_msg_id=start_msg_id)
        count += n
    if count > 0:
        tasks.try_sync_proj_xchat_migrated_msgs.delay(proj.id)
    logger.info('do_migrate_msgs: %s, %s, %s', proj.id, xchat.chat_id, count)


def _do_migrate_msgs(app, key, msgs, start_msg_id, batch_size):
    if len(msgs) > 0:
        domain, type, biz_id = key
        proj = app.projects.filter_by(domain=domain, type=type, biz_id=biz_id).one_or_none()
        if proj:
            _migrate_proj_msgs(proj, msgs, start_msg_id, batch_size)
        else:
            logger.warning('proj not exists: %s, %s, %s', domain, type, biz_id)


@manager.option('-a', '--app_name', type=str, dest="app_name", required=True, help='app name')
@manager.option('-b', '--batch_size', type=int, dest="batch_size", required=False, default=200, help='batch size')
@manager.option('-i', '--start_msg_id', type=int, dest="start_msg_id", required=False, default=1, help='default start msg id')
def migrate_messages(app_name, batch_size, start_msg_id):
    import sys
    from app.service.models import App

    app = App.query.filter_by(name=app_name).one()

    cur_key = None
    msgs = []
    for line in sys.stdin:
        domain, type, biz_id, uid, msg_domain, msg, ts = line.split('\t')
        ts = float(ts)

        key = (domain, type, biz_id)
        if key != cur_key:
            _do_migrate_msgs(app, cur_key, msgs, start_msg_id, batch_size)
            msgs = []
            cur_key = key
        msgs.append(dict(uid=f'{app_name}:{uid}', domain=msg_domain, msg=msg, ts=ts))
    else:
        _do_migrate_msgs(app, cur_key, msgs, start_msg_id, batch_size)


if __name__ == '__main__':
    manager.run()
