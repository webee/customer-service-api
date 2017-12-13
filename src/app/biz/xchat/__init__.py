import logging
import jwt
from datetime import datetime
from app import xchat_client
from app import config
from app.task import tasks
from pytoolbox.jwt import encode_ns_user, decode_ns_user
from .constant import XCHAT_CHAT_TAG
from .constant import CHAT_MSG_KIND, CHAT_NOTIFY_MSG_KIND, XCHAT_NS, XCHAT_APP_ID


logger = logging.getLogger(__name__)


def create_chat(project):
    biz_id = project.xchat_biz_id
    users = [c.app_uid for c in project.customers]
    title = '%s/%s' % (project.domain.name, project.type.name)
    return xchat_client.new_chat(xchat_client.constant.ChatType.GROUP,
                                 users=users,
                                 app_id=XCHAT_APP_ID,
                                 biz_id=biz_id,
                                 start_msg_id=project.start_msg_id,
                                 title=title,
                                 tag=XCHAT_CHAT_TAG
                                 )


def handle_msg_notify(msg):
    kind = msg['kind']
    if kind == 'chat':
        tasks.sync_xchat_msgs.delay(msg)
    elif kind == 'chat_notify':
        pass
        # tasks.notify_xchat_msgs.delay(msg)


def handle_user_statuses(user_statuses):
    tasks.sync_user_statuses.apply_async(args=(user_statuses,), expires=180)


def new_user_jwt(ns, name, exp_delta):
    exp = datetime.utcnow() + exp_delta
    payload = dict(
        ns=ns,
        name=name,
        username=encode_ns_user(ns, name),
        exp=exp
    )

    return jwt.encode(payload, config.XChat.KEY).decode('utf-8'), exp.timestamp()
