from datetime import timedelta


class App:
    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs_dev:cs1234@localhost/cs_beta'
    SQLALCHEMY_ECHO = False


class Biz:
    CLOSED_SESSION_ALIVE_TIME = timedelta(hours=3)


class XChat:
    WS_URL = 'ws://b.xchat.qinqinxiaobao.com/ws'


class XChatClient:
    ROOT_URL = "http://l-b.xchat.com"
