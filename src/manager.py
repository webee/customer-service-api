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
@manager.option('-u', '--uid', type=str, dest="uid", required=True, help='user id')
def new_staff_token(app_name, uid):
    from app.service.models import App
    from app import jwt

    app = App.query.filter_by(name=app_name).one()
    staff = app.staffs.filter_by(uid=uid).one()

    token = jwt.encode_token('staff', staff)
    logger.info('token: %s', token)


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


def _migrate_proj_msgs(proj, msgs, start_msg_id=None, start_delta=None, batch_size=200):
    import arrow
    from sqlalchemy import desc
    from app.utils.commons import batch_split
    from app import xchat_client
    from app.service.models import Message
    from app.task import tasks

    xchat = proj.xchat
    if start_msg_id is not None:
        if xchat.start_msg_id < start_msg_id:
            logger.info('do_migrate_msgs: migrated %s, %s', proj.id, xchat.chat_id)
            return

    rt = arrow.get(msgs[0].ts).datetime
    lt = arrow.get(msgs[-1].ts).datetime

    # 根据时间去掉时间段重复的消息
    lt_msg = proj.messages.filter(Message.ts >= lt, Message.ts <= rt).order_by(Message.ts).first()
    rt_msg = proj.messages.filter(Message.ts >= lt, Message.ts <= rt).order_by(desc(Message.ts)).first()
    if lt_msg and rt_msg:
        l_ts = arrow.get(lt_msg.ts).timestamp
        r_ts = arrow.get(rt_msg.ts).timestamp
        msgs = [msg for msg in msgs if not (l_ts <= msg['ts'] <= r_ts)]

    if len(msgs) <= 0:
        return

    count = 0
    for split_msgs in batch_split(msgs, batch_size):
        ok, n = xchat_client.insert_chat_msgs(xchat.chat_id, split_msgs, start_delta=start_delta)
        start_delta += len(split_msgs)
        if ok:
            count += n
        else:
            break
    if count > 0:
        tasks.try_sync_proj_xchat_migrated_msgs.delay(proj.id)
    logger.info('do_migrate_msgs: %s, %s, %s', proj.id, xchat.chat_id, count)


def _do_migrate_msgs(app, key, msgs, start_msg_id, start_delta, batch_size):
    if len(msgs) <= 0:
        return

    domain, type, biz_id = key
    proj = app.projects.filter_by(domain=domain, type=type, biz_id=biz_id).one_or_none()
    if proj:
        _migrate_proj_msgs(proj, msgs, start_msg_id, start_delta, batch_size)
    else:
        logger.warning('proj not exists: %s, %s, %s', domain, type, biz_id)


def _migrate_msgs_worker(app_name, q):
    from app.service.models import App

    app = App.query.filter_by(name=app_name).one()

    t = q.get()
    while t:
        _do_migrate_msgs(app, *t)
        t = q.get()


@manager.option('-a', '--app_name', type=str, dest="app_name", required=True, help='app name')
@manager.option('-c', '--concurrency', type=int, dest="concurrency", required=False, default=1, help='concurrency')
@manager.option('-b', '--batch_size', type=int, dest="batch_size", required=False, default=200, help='batch size')
@manager.option('-i', '--start_msg_id', type=int, dest="start_msg_id", required=False, default=None,
                help='default start msg id')
@manager.option('-d', '--start_delta', type=int, dest="start_delta", required=False, default=None,
                help='default start delta')
def migrate_messages(app_name, concurrency, batch_size, start_msg_id, start_delta):
    from multiprocessing import Process, Queue
    import sys

    q = Queue(maxsize=concurrency * 4)
    processes = [Process(target=_migrate_msgs_worker, name=f'worker#{i}', args=(app_name, q,)) for i in
                 range(concurrency)]
    for p in processes:
        p.start()

    cur_key = None
    msgs = []
    for line in sys.stdin:
        domain, type, biz_id, uid, msg_domain, msg, ts = line.split('\t')
        ts = float(ts)

        key = (domain, type, biz_id)
        if key != cur_key:
            q.put((cur_key, msgs, start_msg_id, start_delta, batch_size))
            msgs = []
            cur_key = key
        msgs.append(dict(uid=f'{app_name}:{uid}', domain=msg_domain, msg=msg, ts=ts))
    else:
        q.put((cur_key, msgs, start_msg_id, batch_size))

    for _ in processes:
        q.put(None)

    for p in processes:
        p.join()


if __name__ == '__main__':
    manager.run()
