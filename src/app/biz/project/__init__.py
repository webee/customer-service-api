import traceback
import logging
from app import dbs, db, xchat_client
from .utils import TypeMsgPacker
from .ds import parse_xchat_msg_from_data, XChatMessage, MessageData
from app.task import tasks


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
