from app import dbs, xchat_client
from app.service.models import ProjectXChat
from .constant import XCHAT_MSG_TOPIC, XCHAT_CHAT_TAG


@dbs.transactional
def create_project_chat(project):
    biz_id = 'cs:%s' % project.app_biz_id
    users = [c.ns_app_uid for c in project.customers.parties]
    title = '%s/%s' % (project.type.domain.name, project.type.name)
    chat_id = xchat_client.new_chat(xchat_client.constant.ChatType.GROUP,
                                    users=users,
                                    biz_id=biz_id,
                                    mq_topic=XCHAT_MSG_TOPIC,
                                    title=title,
                                    tag=XCHAT_CHAT_TAG
                                    )

    proj_xchat = ProjectXChat.t_query.filter_by(chat_id=chat_id).one_or_none()
    if proj_xchat is None:
        proj_xchat = ProjectXChat(chat_id=chat_id)
    proj_xchat.project = project
    dbs.session.add(proj_xchat)
