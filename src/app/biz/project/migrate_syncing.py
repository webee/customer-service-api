import logging

from app import dbs, xchat_client
from app.biz.ds import parse_xchat_msg_from_data
from app.service.models import ProjectXChat, Message
from app.utils.commons import batch_split
from .commons import syncing_proj_xchat_msgs

logger = logging.getLogger(__name__)


def try_sync_proj_xchat_migrated_msgs(proj_id=None, proj_xchat_id=None, proj=None, proj_xchat=None):
    syncing_proj_xchat_msgs('migrate_syncing', _sync_proj_xchat_migrated_msgs, proj_id=proj_id,
                            proj_xchat_id=proj_xchat_id, proj=proj, proj_xchat=proj_xchat)


def _sync_proj_xchat_migrated_msgs(proj):
    synced_count = 0
    proj_xchat = proj.xchat
    if proj_xchat.start_msg_id <= 0:
        return synced_count

    try:
        msgs, has_more = xchat_client.fetch_chat_msgs(proj_xchat.chat_id, rid=proj_xchat.start_msg_id + 1, limit=100000,
                                                      desc=True)
        for split_msgs in batch_split(msgs, 200):
            _insert_proj_xchat_msg(proj, [parse_xchat_msg_from_data(msg) for msg in split_msgs])
        synced_count += len(msgs)
        if has_more:
            synced_count += _sync_proj_xchat_migrated_msgs(proj)
    except:
        logger.exception('sync proj migrated msgs error: %d', proj.id)

    return synced_count


@dbs.transactional
def _insert_proj_xchat_msg(proj, xchat_msgs):
    msgs = []
    min_msg_id = proj.xchat.start_msg_id
    for xchat_msg in xchat_msgs:
        _, user_type, uid = xchat_msg.app_user_id
        channel, domain, type, content = xchat_msg.msg_data
        msgs.append((xchat_msg.id, channel, domain, type, content, user_type, uid, xchat_msg.ts))

        if xchat_msg.id < min_msg_id:
            min_msg_id = xchat_msg.id

    _insert_messages(proj, msgs)

    # update project xchat msg id
    ProjectXChat.query.filter_by(id=proj.xchat.id).filter(ProjectXChat.start_msg_id >= min_msg_id).update(
        {'start_msg_id': min_msg_id - 1})


def _insert_messages(proj, msgs=()):
    messages = []
    msg_id = None
    for i, msg in enumerate(msgs, 0):
        id, channel, domain, type, content, user_type, user_id, ts = msg
        message = Message(project_id=proj.id, rx_key=id, user_type=user_type, user_id=user_id,
                          msg_id=proj.start_msg_id - i,
                          channel=channel, domain=domain, type=type, content=content, ts=ts)
        messages.append(message)
        msg_id = message.msg_id

    dbs.session.bulk_save_objects(messages)

    # update project start_msg_id
    if msg_id is not None:
        proj.start_msg_id = msg_id - 1
        dbs.session.add(proj)
