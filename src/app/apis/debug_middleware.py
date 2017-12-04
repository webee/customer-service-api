import logging
from flask import request
from . import blueprint as app
from time import time

logger = logging.getLogger(__name__)

MAX_LOG_CONTENT_LENGTH = 64 * 1024


@app.before_request
def record_start_time():
    request.start_time = time()


@app.after_request
def append_process_time(response):
    t = (time() - request.start_time) * 1000
    response.headers['x-p-t'] = t

    return response


@app.before_request
def log_request():
    info = dict(method=request.method, url=request.url)
    if request.content_length is not None and 0 < request.content_length <= 64 * 1024:
        info['data'] = request.get_data()

    logger.debug(info)
