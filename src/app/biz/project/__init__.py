import traceback
import logging
from app import dbs, db, xchat_client
from sqlalchemy import desc as order_desc
from .utils import TypeMsgPacker
from .ds import parse_xchat_msg_from_data, XChatMessage, MessageData
from app.task import tasks
from app.service.models import Message


MAX_MSGS_FETCH_SIZE = 3000;


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


def fetch_session_msgs(session, lid=None, rid=None, limit=None, desc=None):
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

    q = session.messages.filter(Message.msg_id > lid)
    if rid > 0:
        q = q.filter(Message.msg_id < rid)
    q = q.order_by(order_desc(Message.msg_id) if desc else Message.msg_id).limit(limit)
    msgs = q.all()
    has_more = False
    if origin_limit <= 0 or origin_limit > MAX_MSGS_FETCH_SIZE:
        # 没有指定limit或者指定范围超出的情况
        has_more = len(msgs) >= limit

    return msgs, has_more
