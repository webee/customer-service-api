
class Config:
    ROOT_URL = "https://xchat.qinqinxiaobao.com"

    CHATS_PATH = "/api/chats/"
    CHAT_PATH = "/api/chats/{chat_id}/"
    CHAT_MEMBERS_PATH = "/api/chats/{chat_id}.members"

    INSERT_CHAT_MESSAGES_PATH = "/api/chats/{chat_id}/msgs/"

    SEND_MSG_PATH = '/xchat/api/user/msg/send/'
    SEND_USER_NOTIFY_PATH = '/xchat/api/user/notify/send/'

    FETCH_CHAT_MSGS_PATH = "/xchat/api/chats/{chat_id}/msgs"
