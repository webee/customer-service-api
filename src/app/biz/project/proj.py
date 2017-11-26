import arrow
from app import db, dbs, config
from sqlalchemy import orm
from app.service.models import Project, Session, Message


def lock_project(id, options=None, read=False):
    options = [] if options is None else list(options)
    options.append(orm.lazyload('*'))
    return Project.query.options(*options).with_for_update(read=read, of=Project).filter_by(id=id).one()


@dbs.transactional
def try_open_session(proj_id):
    # 锁住project
    proj = lock_project(proj_id, options=[orm.joinedload('last_session'), orm.joinedload('current_session')])
    if proj.current_session is None:
        last_session = proj.last_session
        if last_session is None or arrow.now() - arrow.get(last_session.closed) > config.Biz.CLOSED_SESSION_ALIVE_TIME:
            # 没有上次session或者已经超过存活时间
            proj.current_session = Session(project=proj, handler=proj.staffs.leader,
                                           start_msg_id=proj.msg_id, sync_msg_id=proj.msg_id)

            dbs.session.add(proj)
        else:
            # 重新打开上一次的会话
            last_session.closed = None
            last_session.is_active = True
            proj.current_session = last_session

            dbs.session.add(proj)

    return proj


@dbs.transactional
def close_current_session(proj_id):
    # 锁住project
    proj = lock_project(proj_id, options=[orm.joinedload('current_session')])

    current_session = proj.current_session
    if current_session is not None:
        current_session.is_active = False
        current_session.closed = db.func.current_timestamp()
        dbs.session.add(current_session)

        proj.last_session = current_session
        proj.current_session = None
        dbs.session.add(proj)


@dbs.transactional
def new_messages(proj_id, msgs=()):
    if len(msgs) == 0:
        return

    # open session
    proj = try_open_session(proj_id)
    for i, (domain, type, content, user_type, user_id, ts) in enumerate(msgs, 1):
        message = Message(project=proj, session=proj.current_session,
                          user_type=user_type, user_id=user_id,
                          msg_id=proj.msg_id + i,
                          domain=domain, type=type, content=content,
                          ts=ts)
        dbs.session.add(message)

    # update project & session msg_id
    return __next_msg_id(proj, n=len(msgs))


def __next_msg_id(proj, n=1):
    try_open_session(proj.id)

    proj.msg_id = Project.msg_id + n
    dbs.session.add(proj)
    dbs.session.flush()

    proj.current_session.msg_id = proj.msg_id
    proj.current_session.msg_ts = db.func.current_timestamp()
    dbs.session.add(proj.current_session)

    return proj.msg_id
