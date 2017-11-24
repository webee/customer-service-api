import logging
from flask import request
from . import blueprint as app


logger = logging.getLogger(__name__)


MAX_LOG_CONTENT_LENGTH = 64 * 1024


@app.before_request
def log_request():
    info = dict(method=request.method, url=request.url)
    if request.content_length is not None and 0 < request.content_length <= 64*1024:
        info['data'] = request.get_data()

    logger.debug(info)
