import traceback
import logging
from app import dbs, xchat_client
from app.service.models import ProjectXChat
from .ds import parse_xchat_msg_from_data
from .proj import new_messages

logger = logging.getLogger(__name__)


def sync_xchat_msgs(msg):
    xchat_msg = parse_xchat_msg_from_data(msg)
    proj_xchat = ProjectXChat.query.filter_by(chat_id=xchat_msg.chat_id).one_or_none()
    if proj_xchat is None:
        # 不存在的项目
        return

    if xchat_msg.app_user_id.app_name != proj_xchat.project.app.name:
        # app name不匹配
        return

    if xchat_msg.id <= proj_xchat.msg_id:
        # 已经同步
        return

    try_sync_proj_xchat_msgs(proj_xchat.id, xchat_msg)


def try_sync_proj_xchat_msgs(proj_xchat_id, xchat_msg=None):
    if ProjectXChat.try_sync(proj_xchat_id):
        try:
            while True:
                pending = ProjectXChat.current_pending(proj_xchat_id)
                sync_proj_xchat_msgs(proj_xchat_id, xchat_msg)
                if ProjectXChat.should_sync(proj_xchat_id, pending) or not ProjectXChat.done_sync(proj_xchat_id):
                    continue
                break
        except:
            ProjectXChat.stop_sync(proj_xchat_id)


def sync_proj_xchat_msgs(proj_xchat_id, xchat_msg=None):
    proj_xchat = ProjectXChat.query.filter_by(id=proj_xchat_id).one()
    proj = proj_xchat.project

    if xchat_msg and proj_xchat.msg_id + 1 == xchat_msg.id:
        new_proj_xchat_msg(proj, (xchat_msg,))

    try:
        msgs, has_more = xchat_client.fetch_chat_msgs(proj_xchat.chat_id, lid=proj_xchat.msg_id, limit=5000)
        i = 0
        while i < len(msgs):
            j = i + 75
            new_proj_xchat_msg(proj, [parse_xchat_msg_from_data(msg) for msg in msgs[i:j]])
            i = j
        if has_more:
            sync_proj_xchat_msgs(proj_xchat)
    except:
        logging.error(traceback.format_exc())


@dbs.transactional
def new_proj_xchat_msg(proj, xchat_msgs):
    msgs = []
    max_msg_id = proj.xchat.id
    for xchat_msg in xchat_msgs:
        app_name, user_type, uid = xchat_msg.app_user_id
        domain, type, content = xchat_msg.msg_data
        msgs.append((domain, type, content, user_type, uid))

        if xchat_msg.id > max_msg_id:
            max_msg_id = xchat_msg.id

    new_messages(proj.id, msgs)

    # update project xchat msg id
    ProjectXChat.query.filter_by(id=proj.xchat.id).filter(ProjectXChat.msg_id < max_msg_id).update({'msg_id': max_msg_id})
