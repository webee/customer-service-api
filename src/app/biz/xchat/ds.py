from collections import namedtuple
import arrow
from .constant import XCHAT_NS

AppUserID = namedtuple('AppUserID', ['app_name', 'user_type', 'uid'])
MessageData = namedtuple('MessageData', ['domain', 'type', 'content'])
XChatMessage = namedtuple('XChatMessage', ['chat_id', 'app_user_id', 'id', 'message_data', 'ts'])


def parse_app_user_id_from_xchat_uid(xchat_uid):
    if not xchat_uid.startswith(XCHAT_NS):
        raise Exception('bad xchat cs uid: %s' % xchat_uid)
    app_uid = xchat_uid[len(XCHAT_NS) + 1:]
    return AppUserID(*app_uid.split(':'))


def parse_xchat_message_from_data(data):
    chat_id = data['chat_id']
    id = data.get('id')
    app_user_id = parse_app_user_id_from_xchat_uid(data['uid'])
    msg = data['msg']
    ts = arrow.get(data['ts']).datetime
    msg_domain = data.get('domain', 'cs')

    # 分解消息类型，默认为text
    parts = msg[:30].split(':', 1)
    msg_type = 'text'
    msg_content = msg
    if len(parts) > 1:
        msg_type = parts[0]
        msg_content = msg[len(msg_type) + 1:]

    message_data = MessageData(msg_domain, msg_type, msg_content)

    return XChatMessage(chat_id, app_user_id, id, message_data, ts)
