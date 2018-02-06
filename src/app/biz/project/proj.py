import arrow
from app import db, dbs, config
from sqlalchemy import orm
from app.service.models import Project, Session, Message, UserType
from app.task import tasks
from app.biz.constants import NotifyTypes
from app.biz.notifies import task_project_notify


def lock_project(id, options=None, read=False):
    options = [] if options is None else list(options)
    options.append(orm.lazyload('*'))
    return db.session.query(Project).options(*options).populate_existing().with_for_update(read=read, of=Project).filter_by(id=id).one()


def try_handle_project(proj, handler):
    if proj.current_session is not None and proj.current_session.handler_id == handler.id:
        # 就是当前handler
        return proj
    prev_handler, proj = try_open_session(proj.id, handler)
    # # notify client
    # 1. 通知新接待者添加session
    task_project_notify(proj, NotifyTypes.MY_HANDLING_SESSIONS, dict(sessionID=proj.current_session_id))
    if prev_handler:
        # 2. 通知旧接待者删除session
        current_session = proj.current_session
        handler = current_session.handler
        task_project_notify(proj, NotifyTypes.MY_HANDLING_SESSION_TRANSFERRED,
                            dict(sessionID=current_session.id, uid=handler.uid, name=handler.name),
                            handler=prev_handler)
    return proj


@dbs.transactional
def try_open_session(proj_id, handler=None):
    # 锁住project
    proj = lock_project(proj_id)
    prev_handler = None
    if proj.current_session_id is None:
        handler = proj.leader if handler is None else handler
        if proj.last_session_id is None:
            # 没有上次session
            current_session = Session(project=proj, handler=handler, start_msg_id=proj.msg_id, sync_msg_id=proj.msg_id)
        else:
            last_session = proj.last_session
            if arrow.now() - arrow.get(last_session.closed) > config.Biz.CLOSED_SESSION_ALIVE_TIME:
                # 上次session已经超过存活时间
                if last_session.msg_id > 0:
                    # 有发送过消息
                    current_session = Session(project=proj, handler=handler, start_msg_id=proj.msg_id,
                                              sync_msg_id=proj.msg_id,
                                              activated_channel=last_session.activated_channel,
                                              channel_user_id=last_session.channel_user_id)
                else:
                    # 没有发送过消息
                    # 则重新打开上一次的会话
                    last_session.closed = None
                    last_session.is_active = True
                    last_session.handler = handler
                    last_session.created = db.func.current_timestamp()
                    current_session = last_session
            else:
                # 重新打开上一次的会话
                last_session.closed = None
                last_session.is_active = True
                if handler is not None:
                    last_session.handler = handler
                current_session = last_session

        proj.current_session = current_session
        db.session.add(proj)
    elif handler is not None:
        current_session = proj.current_session
        prev_handler = current_session.handler
        current_session.handler = handler
        db.session.add(current_session)

    return prev_handler, proj


@dbs.transactional
def close_current_session(proj_id, session_id=None):
    # 锁住project
    proj = lock_project(proj_id)

    if proj.current_session_id is not None and proj.current_session_id == session_id:
        current_session = proj.current_session
        current_session.is_active = False
        current_session.closed = db.func.current_timestamp()
        db.session.add(current_session)

        proj.last_session = current_session
        proj.current_session = None
        db.session.add(proj)
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
    msg_id = None
    handler_msg_id = None
    for i, msg in enumerate(msgs, 1):
        id, channel, domain, type, content, user_type, user_id, ts = msg
        message = Message(project_id=proj.id, session_id=current_session.id,
                          rx_key=id,
                          user_type=user_type, user_id=user_id,
                          msg_id=proj.msg_id + i,
                          channel=channel, domain=domain, type=type, content=content, ts=ts)
        messages.append(message)

        msg_id = message.msg_id
        if user_type == UserType.staff:
            handler_msg_id = message.msg_id
            if activated_channel:
                channel_msgs.append((proj.app_name, activated_channel, channel_user_id, user_id, type, content,
                                     dict(domain=proj.domain, type=proj.type, biz_id=proj.biz_id, id=proj.id)))
        elif user_type == UserType.customer:
            has_user_msg = True
            activated_channel = channel
            if activated_channel is not None:
                channel_user_id = user_id
            else:
                channel_user_id = None

    db.session.bulk_save_objects(messages)

    tasks.send_channel_msgs.delay(channel_msgs)

    # update project & session msg_id
    if msg_id is not None:
        proj.msg_id = msg_id
    db.session.add(proj)

    if has_user_msg:
        proj.current_session.activated_channel = activated_channel
        proj.current_session.channel_user_id = channel_user_id
    proj.current_session.msg_id = proj.msg_id
    if handler_msg_id is not None:
        proj.current_session.handler_msg_id = handler_msg_id
    db.session.add(proj.current_session)
