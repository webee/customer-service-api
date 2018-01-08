from datetime import timedelta


class App:
    TESTING = True

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs_dev:cs1234@localhost/cs_test'
    SQLALCHEMY_ECHO = False


class XChat:
    WS_URL = 'ws://t.xchat.qinqinxiaobao.com/ws'


class XChatClient:
    ROOT_URL = "http://l-t.xchat.com"
