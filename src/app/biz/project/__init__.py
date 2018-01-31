import logging
import arrow

from sqlalchemy import desc as order_desc, func, or_
from sqlalchemy.orm import lazyload

from app import config
from app import dbs, xchat_client
from app.biz.constants import NotifyTypes
from app.biz.notifies import task_project_notify
from app.biz.utils import TypeMsgPacker, ChannelDomainPacker
from app.service import path_labels
from app.service.models import Message, Session, Project
from app.task import tasks
from .proj import close_current_session

MAX_MSGS_FETCH_SIZE = 3000
DEFAULT_MSGS_FETCH_SIZE = 256

logger = logging.getLogger(__name__)


def send_channel_message(proj, customer, channel, domain, type, content):
    proj_xchat = proj.xchat
    chat_id = proj_xchat.chat_id
    user = customer.app_uid

    return _send_message(chat_id, user, channel, domain, type, content)


def send_message(proj, staff, domain, type, content):
    # 1. 发送到xchat
    proj_xchat = proj.xchat
    chat_id = proj_xchat.chat_id
    user = staff.app_uid

    return _send_message(chat_id, user, None, domain, type, content)


def _send_message(chat_id, user, channel, domain, type, content):
    # 1. 发送到xchat
    domain = ChannelDomainPacker.pack(domain, channel=channel)
    msg = TypeMsgPacker.pack(type, content)
    id, ts = xchat_client.send_chat_msg(chat_id, user, msg, domain=domain)

    msg_data = dict(chat_id=chat_id, id=id, ts=ts, user=f'{config.App.NAME}:{user}', msg=msg, domain=domain)
    # 2. send celery task request
    tasks.sync_xchat_msgs.delay(msg_data)

    # rx_key, ts
    return id, ts


def sync_session_msg_id(staff, session, msg_id):
    with dbs.require_transaction_context():
        ret = Session.query.filter_by(id=session.id) \
            .filter(Session.handler_id == staff.id,
                    Session.is_active == True,
                    Session.msg_id >= msg_id,
                    Session.sync_msg_id < msg_id).update({'sync_msg_id': msg_id})

    if ret:
        # # notify client
        task_project_notify(session.project, NotifyTypes.MY_HANDLING_SESSIONS, dict(sessionID=session.id))


def fetch_ext_data(staff, proj):
    ext_data_updated = proj.ext_data_updated
    if ext_data_updated is None or arrow.now() - arrow.get(ext_data_updated) > config.Biz.FETCH_EXT_DATA_INTERVAL:
        tasks.fetch_ext_data.delay(proj.app.name, proj.domain, proj.type, proj.biz_id, id=proj.id, staff_uid=staff.uid)


def finish_session(staff, session):
    if close_current_session(session.project_id, session_id=session.id):
        # # notify client
        task_project_notify(session.project, NotifyTypes.MY_HANDLING_SESSION_FINISHED, dict(sessionID=session.id),
                            handler=staff)


def fetch_project_msgs(project, lid=None, rid=None, limit=None, desc=None):
    if lid is None:
        lid = 0
        if desc is None:
            desc = True

    if rid is None:
        rid = 0

    if lid > 0 and 0 < rid <= lid + 1:
        return [], False

    if desc is None:
        desc = False

    if limit is None:
        limit = 0

    origin_limit = limit
    if lid > 0 and rid > 0:
        origin_limit = rid - lid - 1

    if limit <= 0:
        limit = DEFAULT_MSGS_FETCH_SIZE
    elif limit > MAX_MSGS_FETCH_SIZE:
        limit = MAX_MSGS_FETCH_SIZE

    # 这里不需要用到Session
    # TODO: 研究生成复杂sql的原因是什么？
    # q = project.messages.options(lazyload('project'), lazyload('session')).filter(Message.msg_id > lid)
    q = Message.query.options(lazyload('project', 'session')).filter_by(project_id=project.id).filter(Message.msg_id > lid)
    if rid > 0:
        q = q.filter(Message.msg_id < rid)
    q = q.order_by(order_desc(Message.msg_id) if desc else Message.msg_id).limit(limit)
    msgs = q.all()
    # has_more指本次请求是否未完成，no_more指集合是否还有数据
    has_more = False
    if origin_limit <= 0 or origin_limit > MAX_MSGS_FETCH_SIZE:
        # 没有指定limit或者指定范围超出的情况
        has_more = len(msgs) >= limit
    no_more = len(msgs) < limit

    return msgs, has_more, no_more


# permissions
def staff_has_perm_for_project(staff, proj):
    return staff.id == proj.leader_id or (
        proj.current_session is not None and proj.current_session.handler_id == staff.id
    ) or path_labels.scopes_match_ctxes(
        proj.scope_labels, staff.uid,
        staff.context_labels)


def get_staff_project(staff, id):
    return staff.app.projects.filter_by(id=id) \
        .filter(or_(Project.leader_id == staff.id,
                    func.x_scopes_match_ctxes(Project.scope_labels,
                                              staff.uid,
                                              staff.context_labels),
                    Project.current_session.has(Session.handler_id == staff.id)
                    )).one()
