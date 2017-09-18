import logging
from app import xchat_client
from app import dbs
from sqlalchemy.orm import lazyload, joinedload, subqueryload
from .constant import XCHAT_MSG_TOPIC, XCHAT_CHAT_TAG
from .constant import CHAT_MSG_KIND, CHAT_NOTIFY_MSG_KIND, XCHAT_NS
from app.service.models import ProjectXChat, Session, Project, Message, UserType, MessageChannel
from . import ds


logger = logging.getLogger(__name__)


def create_chat(project):
    biz_id = project.xchat_biz_id
    users = [c.app_uid for c in project.customers.parties]
    title = '%s/%s' % (project.domain.name, project.type.name)
    return xchat_client.new_chat(xchat_client.constant.ChatType.GROUP,
                                 users=users,
                                 biz_id=biz_id,
                                 mq_topic=XCHAT_MSG_TOPIC,
                                 title=title,
                                 tag=XCHAT_CHAT_TAG
                                 )


@dbs.transactional
def new_xchat_msg(xchat_msg: ds.XChatMessage):
    proj_xchat = ProjectXChat.query.filter_by(chat_id=xchat_msg.chat_id).one_or_none()
    if proj_xchat is None:
        return

    proj = proj_xchat.project
    if proj.messages.filter_by(xchat_id=xchat_msg.id).count() > 0:
        # 忽略已经添加过的
        return

    app = proj.app
    app_name, user_type, uid = xchat_msg.app_user_id
    assert app.name == app_name, 'app_user_id and app_name are mismatched'

    user_type = UserType(user_type)
    customer = None
    staff = None
    if user_type is UserType.customer:
        customer = app.customers.filter_by(uid=uid).one()
    elif user_type is UserType.staff:
        staff = app.staffs.filter_by(uid=uid).one()

    proj = dbs.session.query(Project).options(lazyload('*')).with_for_update(read=False).filter_by(id=proj.id).one()
    msg_id = proj.next_msg_id()
    session = proj.current_session
    message_data: ds.MessageData = xchat_msg.message_data
    message = Message(channel=MessageChannel.xchat,
                      project=proj, session=session, msg_id=msg_id,
                      xchat_id=xchat_msg.id,
                      user_type=user_type, customer=customer, staff=staff,
                      domain=message_data.domain, type=message_data.type, content=message_data.type,
                      ts=xchat_msg.ts)
    dbs.session.add(message)


def handle_xchat_msg(data):
    """处理来自xchat的转发消息"""
    kind = data['kind']
    if kind == CHAT_MSG_KIND:
        # 会话消息
        new_xchat_msg(ds.parse_xchat_message_from_data(data))
    elif kind == CHAT_NOTIFY_MSG_KIND:
        # 会话通知
        # TODO
        pass
