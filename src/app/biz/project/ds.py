from collections import namedtuple
import arrow
from .utils import TypeMsgPacker


AppUserID = namedtuple('AppUserID', ['app_name', 'user_type', 'uid'])
MessageData = namedtuple('MessageData', ['domain', 'type', 'content'])
XChatMessage = namedtuple('XChatMessage', ['chat_id', 'app_user_id', 'id', 'msg_data', 'ts'])


def parse_app_user_id_from_xchat_uid(xchat_uid):
    if not xchat_uid.startswith('cs'):
        raise Exception('bad xchat cs uid: %s' % xchat_uid)
    app_uid = xchat_uid[len('cs') + 1:]
    return AppUserID(*app_uid.split(':'))


def parse_xchat_msg_from_data(data):
    chat_id = data['chat_id']
    id = data.get('id')
    app_user_id = parse_app_user_id_from_xchat_uid(data['user'])
    msg = data['msg']
    ts = arrow.get(data['ts']).datetime
    msg_domain = data.get('domain', '')

    msg_type = TypeMsgPacker.unpack(msg)
    msg_content = msg[len(msg_type) + 1:] if msg_type is not None else msg
    msg_type = msg_type if msg_type is not None else ''

    message_data = MessageData(msg_domain, msg_type, msg_content)

    return XChatMessage(chat_id, app_user_id, id, message_data, ts)
