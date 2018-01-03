import arrow
from app import db, dbs, config
from sqlalchemy import orm
from app.service.models import Project, Session, Message, UserType
from app.task import tasks


def lock_project(id, options=None, read=False):
    options = [] if options is None else list(options)
    options.append(orm.lazyload('*'))
    return Project.query.options(*options).with_for_update(read=read, of=Project).filter_by(id=id).one()


def try_handle_project(proj, handler):
    if proj.current_session is not None and proj.current_session.handler_id == handler.id:
        # 就是当前handler
        return proj
    prev_handler, proj = try_open_session(proj.id, handler)
    # TODO: 1. 通知新接待者添加session
    # TODO: 2. 通知旧接待者删除session
    return proj


@dbs.transactional
def try_open_session(proj_id, handler=None):
    # 锁住project
    proj = lock_project(proj_id, options=[orm.joinedload('last_session'), orm.joinedload('current_session')])
    prev_handler = None
    if proj.current_session is None:
        last_session = proj.last_session
        if last_session is None or arrow.now() - arrow.get(last_session.closed) > config.Biz.CLOSED_SESSION_ALIVE_TIME:
            # 没有上次session或者已经超过存活时间
            proj.current_session = Session(project=proj, handler=proj.leader if handler is None else handler,
                                           start_msg_id=proj.msg_id, sync_msg_id=proj.msg_id)

            dbs.session.add(proj)
        else:
            # 重新打开上一次的会话
            last_session.closed = None
            last_session.is_active = True
            if handler is not None:
                last_session.handler = handler
            proj.current_session = last_session

            dbs.session.add(proj)
    elif handler is not None:
        current_session = proj.current_session
        prev_handler = current_session.handler
        current_session.handler = handler
        dbs.session.add(current_session)

    return prev_handler, proj


@dbs.transactional
def close_current_session(proj_id, session_id=None):
    # 锁住project
    proj = lock_project(proj_id, options=[orm.joinedload('current_session')])

    current_session = proj.current_session
    if current_session is not None and current_session.id == session_id:
        current_session.is_active = False
        current_session.closed = db.func.current_timestamp()
        dbs.session.add(current_session)

        proj.last_session = current_session
        proj.current_session = None
        dbs.session.add(proj)
        return True
    return False


@dbs.transactional
def new_messages(proj_id, msgs=()):
    # open session
    _, proj = try_open_session(proj_id)
    current_session = proj.current_session
    messages = []
    has_user_msg = False
    activated_channel = current_session.activated_channel
    channel_user_id = current_session.channel_user_id
    channel_msgs = []
    for i, msg in enumerate(msgs, 1):
        id, channel, domain, type, content, user_type, user_id, ts = msg
        messages.append(Message(project_id=proj.id, session_id=current_session.id,
                                rx_key=id,
                                user_type=user_type, user_id=user_id,
                                msg_id=proj.msg_id + i,
                                channel=channel, domain=domain, type=type, content=content, ts=ts))

        if user_type == UserType.staff and activated_channel:
            channel_msgs.append((proj.app_name, activated_channel, channel_user_id, user_id, type, content,
                                 dict(domain=proj.domain, type=proj.type, biz_id=proj.biz_id, id=proj.id)))
        elif user_type == UserType.customer:
            has_user_msg = True
            activated_channel = channel
            if channel is not None:
                channel_user_id = user_id

    dbs.session.bulk_save_objects(messages)

    tasks.send_channel_msgs.delay(channel_msgs)
    # update project & session msg_id
    return __next_msg_id(proj, len(msgs), has_user_msg, activated_channel, channel_user_id)


def __next_msg_id(proj, n=1, has_user_msg=False, activated_channel=None, channel_user_id=None):
    proj.msg_id = Project.msg_id + n
    dbs.session.add(proj)
    dbs.session.flush()

    if has_user_msg:
        proj.current_session.activated_channel = activated_channel
        proj.current_session.channel_user_id = channel_user_id
    proj.current_session.msg_id = proj.msg_id
    dbs.session.add(proj.current_session)

    return proj.msg_id
