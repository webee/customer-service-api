from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def success(**kwargs):
    logger.info("response: [{0}]".format(kwargs))
    return jsonify(ret=True, **kwargs)


def _fail(code=1, msg='fail', **kwargs):
    logger.info(msg)
    return jsonify(ret=False, code=code, msg=msg, **kwargs)


def fail(msg='fail', code=1, **kwargs):
    return _fail(code, msg, **kwargs), 499


def bad_request(msg='bad request', code=400, **kwargs):
    return _fail(code, msg, **kwargs), 400


def processed(code=202, msg='processed', **kwargs):
    return _fail(code, msg, **kwargs), code


def not_found(code=404, msg='not found.', **kwargs):
    return _fail(code, msg, **kwargs), code


def accepted(**kwargs):
    return success(**kwargs), 202


def refused(code=403, msg='refused', **kwargs):
    return _fail(code, msg, **kwargs), code


def error(code=500, msg='error', **kwargs):
    return _fail(code, msg, **kwargs), code
