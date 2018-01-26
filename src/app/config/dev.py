from datetime import timedelta


class App:
    pass


class Biz:
    # 已经结束的会话的复活最大时间间隔
    CLOSED_SESSION_ALIVE_TIME = timedelta(minutes=3)
