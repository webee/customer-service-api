class MethodType:
    GET_TOKEN = 'getToken'
    GET_EXT_DATA = 'getExtData'
    ACCESS_FUNCTION = 'accessFunction'
    SEND_CHANNEL_MSG = 'sendChannelMsg'
    PUSH_MSG = 'pushMsg'


PARAM_HEADER_MAP = {
    'appid': 'X-App-Id',
    'appkey': 'X-App-Key',
    'token': 'X-Token',
}


class ErrorCode:
    AUTH_FAILED = 1
    TOKEN_EXPIRED = 2
    INVALID_TOKEN = 3
    REQUEST_FAILED = 99
