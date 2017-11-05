import traceback
import logging
from app import dbs, db, xchat_client
from app.service.models import Project, UserType, Message, Session, ProjectXChat
from .ds import parse_xchat_msg_from_data, XChatMessage, MessageData
from .proj import new_message

logger = logging.getLogger(__name__)


def try_sync_xchat_msgs(msg):
    xchat_msg = parse_xchat_msg_from_data(msg)
    proj_xchat = ProjectXChat.query.filter_by(chat_id=xchat_msg.chat_id).one_or_none()
    if proj_xchat is None:
        # 不存在的项目
        return

    if xchat_msg.id <= proj_xchat.msg_id:
        # 已经同步
        return

    if proj_xchat.try_sync():
        while True:
            pending = proj_xchat.current_pending()
            sync_proj_xchat_msgs(proj_xchat, xchat_msg)
            if proj_xchat.should_sync(pending) or not proj_xchat.done_sync():
                continue
            break


def sync_proj_xchat_msgs(proj_xchat, xchat_msg=None):
    proj = proj_xchat.project

    if xchat_msg and proj_xchat.msg_id + 1 == xchat_msg.id:
        new_proj_xchat_msg(proj, xchat_msg)

    try:
        msgs, has_more = xchat_client.fetch_chat_msgs(proj_xchat.chat_id, lid=proj_xchat.msg_id, limit=5000)
        # TODO: 适当批量创建
        for msg in msgs:
            new_proj_xchat_msg(proj, parse_xchat_msg_from_data(msg))
        if has_more:
            sync_proj_xchat_msgs(proj_xchat)
    except:
        logging.error(traceback.format_exc())


@dbs.transactional
def new_proj_xchat_msg(proj, xchat_msg: XChatMessage):
    app = proj.app
    app_name, user_type, uid = xchat_msg.app_user_id
    if app.name != app_name:
        return

    user_type = UserType(user_type)
    customer = None
    staff = None
    if user_type is UserType.customer:
        customer = app.customers.filter_by(uid=uid).one()
    elif user_type is UserType.staff:
        staff = app.staffs.filter_by(uid=uid).one()

    msg_data: MessageData = xchat_msg.msg_data
    new_message(proj, msg_data.domain, msg_data.type, msg_data.content,
                user_type=user_type, customer=customer, staff=staff)

    # update project xchat msg id
    dbs.session.query(ProjectXChat).filter(ProjectXChat.id == proj.xchat.id, ProjectXChat.msg_id < xchat_msg.id) \
        .update({ProjectXChat.msg_id: xchat_msg.id})
