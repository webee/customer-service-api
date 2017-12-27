import logging
import traceback

logger = logging.getLogger(__name__)


class BizError(Exception):
    def __init__(self, code, description, details, status_code=409, headers=None):
        """
        业务异常
        :param code: 错误码
        :param description: 错误信息
        :param details: 错误详情
        :param status_code: http response status code
        :param headers: http response headers
        """
        self.code = code
        self.message = _ERROR_MSGS.get(code)
        self.description = description
        self.details = details
        self.status_code = status_code
        self.headers = headers or {}

    def __repr__(self):
        return 'BizError<%s, %s, %s>' % (self.code, self.message, self.description)

    def __str__(self):
        return 'BizError<%s, %s, %s>' % (self.code, self.message, self.description)


def biz_error_handler(err: BizError):
    logger.error(traceback.format_exc())
    return dict(code=err.code, message=err.message, description=err.description, details=err.details), err.status_code, err.headers


def db_not_found_error_handler(err):
    logger.warning(traceback.format_exc())
    return dict(message='item not found'), 404


def db_found_multi_error_handler(err):
    logger.warning(traceback.format_exc())
    return dict(message='multi items found'), 400


# error msgs and code
_ERROR_MSGS = {
}


def with_error_msg(code, msg):
    _ERROR_MSGS[code] = msg
    return code


# codes
ERR_ITEM_NOT_FOUND = with_error_msg(1000001, 'item not found')
ERR_INVALID_PARAMS = with_error_msg(1000002, 'invalid params')
ERR_PERMISSION_DENIED = with_error_msg(1000100, 'permission denied')
ERR_XXX = with_error_msg(999999, 'xxx')
