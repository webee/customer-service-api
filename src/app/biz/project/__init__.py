import logging

from sqlalchemy import desc as order_desc

from app import dbs, xchat_client
from app.biz.utils import TypeMsgPacker
from app.service.models import Message, Session
from app.task import tasks

MAX_MSGS_FETCH_SIZE = 3000

logger = logging.getLogger(__name__)


def send_message(staff, session, domain, type, content):
    # 发送到xchat
    proj_xchat = session.project.xchat
    chat_id = proj_xchat.chat_id
    user = staff.app_uid
    msg = TypeMsgPacker.pack(type, content)
    id, ts = xchat_client.send_chat_msg(chat_id, user, msg, domain=domain)

    msg_data = dict(chat_id=chat_id, id=id, ts=ts, user='cs:%s' % user, msg=msg, domain=domain)
    # send celery task request
    tasks.sync_xchat_msgs.delay(msg_data)


def sync_session_msg_id(staff, session, msg_id):
    with dbs.require_transaction_context():
        Session.query.filter_by(id=session.id) \
            .filter(Session.handler_id == staff.id,
                    Session.is_active == True,
                    Session.msg_id >= msg_id,
                    Session.sync_msg_id < msg_id).update({'sync_msg_id': msg_id})

    # # notify client
    project = session.project
    # my_handling.session
    tasks.notify_client.delay(staff.app_uid, 'project', 'my_handling.sessions',
                              dict(projectDomain=project.domain.name, projectType=project.type.name,
                                   sessionID=session.id))


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
        limit = 256
    elif limit > MAX_MSGS_FETCH_SIZE:
        limit = MAX_MSGS_FETCH_SIZE

    q = project.messages.filter(Message.msg_id > lid)
    if rid > 0:
        q = q.filter(Message.msg_id < rid)
    q = q.order_by(order_desc(Message.msg_id) if desc else Message.msg_id).limit(limit)
    msgs = q.all()
    has_more = False
    if origin_limit <= 0 or origin_limit > MAX_MSGS_FETCH_SIZE:
        # 没有指定limit或者指定范围超出的情况
        has_more = len(msgs) >= limit

    return msgs, has_more
