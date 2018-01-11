import logging


def _get_logger(name='main', level=logging.INFO):
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.propagate = False
    if len(_logger.handlers) > 0:
        return _logger

    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - [%(name)s.%(levelname)s] [%(threadName)s, %(module)s.%(funcName)s@%(lineno)d] %(message)s')
    ch.setFormatter(formatter)

    _logger.addHandler(ch)

    return _logger

_logger = _get_logger("gunicorn", logging.INFO)


def on_starting(server):
    _logger.info("starting...")


def post_fork(server, worker):
    _logger.info("post fork")


# settings
worker_connections = 2000
max_requests = 10000
max_requests_jitter = 100
timeout = 60
graceful_timeout = 30
keep_alive = 10
access_log_format = '''%(h)s %(l)s %(u)s %(t)s %({Host}i)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'''
