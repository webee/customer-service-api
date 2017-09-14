from app import xchat_client
from .constant import XCHAT_MSG_TOPIC, XCHAT_CHAT_TAG


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
