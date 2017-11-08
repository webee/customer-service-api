from datetime import timedelta


class App:
    DEBUG = False
    TESTING = True

    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://cs_dev:cs1234@localhost/cs_test'


class Biz:
    CLOSED_SESSION_ALIVE_TIME = timedelta(hours=1)


class XChatClient:
    ROOT_URL = "http://l-t.xchat.com"
