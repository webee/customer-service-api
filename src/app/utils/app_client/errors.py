class MethodTypeNotSupportedError(Exception):
    """接口类型不支持"""

    def __init__(self, type):
        super().__init__('method type not supported: %s' % type)


class RequestError(Exception):
    """http请求错误"""

    def __init__(self, resp):
        self.resp = resp
        super().__init__('request error: %d' % self.resp.status_code)


class RequestFailedError(Exception):
    """请求执行失败"""

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        super().__init__('request failed: [%d, %s]' % (code, msg))


class RequestAuthFailedError(RequestFailedError):
    """请求认证失败"""

    def __init__(self, code, msg):
        super().__init__(code, msg)


class RequestTokenError(Exception):
    """请求token错误"""

    def __init__(self, error):
        self.error = error
        super().__init__('request token error')
