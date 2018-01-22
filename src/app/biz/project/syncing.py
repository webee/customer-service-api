import logging

from app import dbs, xchat_client
from app.biz.ds import parse_xchat_msg_from_data
from app.biz.constants import NotifyTypes
from app.biz.notifies import task_project_notify
from app.service.models import Project, ProjectXChat
from app.utils.commons import batch_split
from .proj import new_messages
from .commons import syncing_proj_xchat_msgs

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
    syncing_proj_xchat_msgs('syncing', _sync_proj_xchat_msgs, proj_id=proj_id, proj_xchat_id=proj_xchat_id, proj=proj,
                            proj_xchat=proj_xchat,
                            extra_sync_kwargs=dict(xchat_msg=xchat_msg), done_syncing_func=_done_syncing)


def _done_syncing(synced_count, proj):
    # # notify client
    if synced_count > 0 and proj.current_session_id is not None:
        task_project_notify(proj, NotifyTypes.MSGS, dict(projectID=proj.id))
        task_project_notify(proj, NotifyTypes.MY_HANDLING_SESSIONS, dict(sessionID=proj.current_session_id))


def _sync_proj_xchat_msgs(proj, xchat_msg=None):
    proj_xchat = proj.xchat

    synced_count = 0
    if xchat_msg and proj_xchat.msg_id + 1 == xchat_msg.id:
        _new_proj_xchat_msg(proj, (xchat_msg,))
        synced_count += 1

    try:
        msgs, has_more = xchat_client.fetch_chat_msgs(proj_xchat.chat_id, lid=proj_xchat.msg_id, limit=10000)
        for split_msgs in batch_split(msgs, 100):
            _new_proj_xchat_msg(proj, [parse_xchat_msg_from_data(msg) for msg in split_msgs])
        synced_count += len(msgs)
        if has_more:
            synced_count += _sync_proj_xchat_msgs(proj)
    except:
        logger.exception('sync proj msgs error: %d', proj.id)

    return synced_count


@dbs.transactional
def _new_proj_xchat_msg(proj, xchat_msgs):
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
