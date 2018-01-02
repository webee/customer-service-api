from collections import namedtuple

import arrow

from app.biz.utils import TypeMsgPacker, ChannelDomainPacker

AppUserID = namedtuple('AppUserID', ['app_name', 'user_type', 'uid'])
MessageData = namedtuple('MessageData', ['channel', 'domain', 'type', 'content'])
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

    channel, msg_domain = ChannelDomainPacker.unpack(data.get('domain', ''))
    msg_type, msg_content = TypeMsgPacker.unpack(msg)

    message_data = MessageData(channel, msg_domain, msg_type, msg_content)

    return XChatMessage(chat_id, app_user_id, id, message_data, ts)
