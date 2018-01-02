import logging
import traceback
import time
from app import dbs, xchat_client
from app.biz.ds import parse_xchat_msg_from_data
from app.service.models import Project, ProjectXChat
from app.utils.commons import batch_split
from .constants import NotifyTypes
from app.biz.notifies import task_project_notify
from .proj import new_messages

logger = logging.getLogger(__name__)


def sync_xchat_msgs(msg):
    xchat_msg = parse_xchat_msg_from_data(msg)
    proj_xchat = ProjectXChat.query.filter_by(chat_id=xchat_msg.chat_id).one_or_none()
    if proj_xchat is None:
        # 不存在的项目
        return

    proj = proj_xchat.project
    app = proj.app
    if xchat_msg.app_user_id.app_name != app.name:
        # app name不匹配
        return

    if xchat_msg.id <= proj_xchat.msg_id:
        # 已经同步
        return

    try_sync_proj_xchat_msgs(proj=proj, xchat_msg=xchat_msg)


def try_sync_proj_xchat_msgs(proj_id=None, proj_xchat_id=None, xchat_msg=None, proj=None, proj_xchat=None):
    if proj is not None:
        proj_xchat_id = proj.xchat.id
    elif proj_xchat is not None:
        proj = proj_xchat.project
        proj_xchat_id = proj_xchat.id
    elif proj_id is not None:
        proj = Project.query.filter_by(id=proj_id).one()
        proj_xchat_id = proj.xchat.id
    elif proj_xchat_id is not None:
        proj_xchat = ProjectXChat.query.filter_by(id=proj_xchat_id).one()
        proj = proj_xchat.project
        proj_xchat_id = proj_xchat.id
    else:
        return

    if ProjectXChat.try_sync(proj_xchat_id):
        try:
            synced_count = 0
            while True:
                pending = ProjectXChat.current_pending(proj_xchat_id)
                synced_count += _sync_proj_xchat_msgs(proj, xchat_msg)
                xchat_msg = None
                if not ProjectXChat.done_sync(proj_xchat_id, pending=pending):
                    # 延时累积
                    time.sleep(0.12)
                    continue
                break
            # # notify client
            if synced_count > 0 and proj.current_session_id is not None:
                task_project_notify(proj, NotifyTypes.MSGS, dict(projectID=proj.id))
                task_project_notify(proj, NotifyTypes.MY_HANDLING_SESSIONS, dict(sessionID=proj.current_session_id))
        except:
            ProjectXChat.stop_sync(proj_xchat_id)


def _sync_proj_xchat_msgs(proj, xchat_msg=None):
    proj_xchat = proj.xchat

    synced_count = 0
    if xchat_msg and proj_xchat.msg_id + 1 == xchat_msg.id:
        new_proj_xchat_msg(proj, (xchat_msg,))
        synced_count += 1

    try:
        msgs, has_more = xchat_client.fetch_chat_msgs(proj_xchat.chat_id, lid=proj_xchat.msg_id, limit=5000)
        for split_msgs in batch_split(msgs, 100):
            new_proj_xchat_msg(proj, [parse_xchat_msg_from_data(msg) for msg in split_msgs])
        synced_count += len(msgs)
        if has_more:
            synced_count += _sync_proj_xchat_msgs(proj)
    except:
        logging.error(traceback.format_exc())

    return synced_count


@dbs.transactional
def new_proj_xchat_msg(proj, xchat_msgs):
    msgs = []
    max_msg_id = proj.xchat.msg_id
    for xchat_msg in xchat_msgs:
        _, user_type, uid = xchat_msg.app_user_id
        channel, domain, type, content = xchat_msg.msg_data
        msgs.append((xchat_msg.id, channel, domain, type, content, user_type, uid, xchat_msg.ts))

        if xchat_msg.id > max_msg_id:
            max_msg_id = xchat_msg.id

    new_messages(proj.id, msgs)

    # update project xchat msg id
    ProjectXChat.query.filter_by(id=proj.xchat.id).filter(ProjectXChat.msg_id < max_msg_id).update(
        {'msg_id': max_msg_id})
