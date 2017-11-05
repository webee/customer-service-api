import arrow
from app import db, dbs, config
from sqlalchemy.orm import lazyload, joinedload, subqueryload
from app.service.models import Project, Session, Message


@dbs.transactional
def new_session(proj_id):
    # 锁住project
    proj = dbs.session.query(Project).options(lazyload('*')).with_for_update(read=False).filter_by(id=proj_id).one()
    if proj.current_session is None:
        if proj.last_session is None or arrow.now() - arrow.get(proj.last_session.closed) > config.Biz.CLOSED_SESSION_ALIVE_TIME:
            # 没有上次session或者已经超过存活时间
            proj.current_session = Session(project=proj, handler=proj.staffs.leader, start_msg_id=proj.msg_id)

            dbs.session.add(proj)
        else:
            # 重新打开上一次的会话
            last_session = proj.last_session
            last_session.closed = None
            last_session.is_active = True
            proj.current_session = last_session

            dbs.session.add(proj)

    return proj.current_session


@dbs.transactional
def close_current_session(proj_id):
    # 锁住project
    proj = dbs.session.query(Project).options(lazyload('*')).with_for_update(read=False).filter_by(id=proj_id).one()

    current_session = proj.current_session
    if current_session is not None:
        current_session.is_active = False
        current_session.closed = db.func.current_timestamp()
        dbs.session.add(current_session)

        proj.last_session = current_session
        proj.current_session = None
        dbs.session.add(proj)


@dbs.transactional
def next_msg_id(proj):
    if proj.current_session is None:
        new_session(proj.id)

    proj.msg_id = Project.msg_id + 1
    dbs.session.add(proj)
    dbs.session.flush()

    proj.current_session.msg_id = proj.msg_id
    dbs.session.add(proj.current_session)

    return proj.msg_id


@dbs.transactional
def new_message(proj, domain, type, content, user_type=None, customer=None, staff=None):
    # 锁住project
    proj = dbs.session.query(Project).options(lazyload('*')).with_for_update(read=False).filter_by(id=proj.id).one()
    msg_id = next_msg_id(proj)
    session = proj.current_session
    message = Message(project=proj, session=session, msg_id=msg_id,
                      user_type=user_type, customer=customer, staff=staff,
                      domain=domain, type=type, content=content,
                      ts=db.func.current_timestamp())
    dbs.session.add(message)
    dbs.session.flush()

    return message
