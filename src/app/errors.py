import logging

logger = logging.getLogger(__name__)


class BizError(Exception):
    def __init__(self, msg, details, status_code, code=None, headers=None):
        self.msg = msg
        self.details = details
        self.status_code = status_code
        self.code = code or status_code
        self.headers = headers

    def __repr__(self):
        return 'BizError: %s' % self.msg

    def __str__(self):
        return '%s. %s' % (self.msg, self.details)


def biz_error_handler(error):
    logger.error(error)
    return dict(message=error.msg, code=error.code, details=error.details), error.status_code, error.headers
