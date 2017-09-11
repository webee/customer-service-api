import logging
import traceback

logger = logging.getLogger(__name__)


class BizError(Exception):
    def __init__(self, msg, details, status_code, code=None, headers=None):
        """
        业务异常
        :param msg: 错误信息
        :param details: 错误详情
        :param status_code: http response status code
        :param code: 错误码
        :param headers: http response headers
        """
        self.msg = msg
        self.details = details
        self.status_code = status_code
        self.code = code or status_code
        self.headers = headers

    def __repr__(self):
        return 'BizError: %s' % self.msg

    def __str__(self):
        return '%s. %s' % (self.msg, self.details)


def biz_error_handler(err):
    logger.error(traceback.format_exc())
    return dict(message=err.msg, code=err.code, details=err.details), err.status_code, err.headers


def db_not_found_error_handler(err):
    logger.warning(traceback.format_exc())
    return dict(message='item not found'), 404
