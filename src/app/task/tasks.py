import logging
from . import app
from app.biz.project import sync


logger = logging.getLogger(__name__)


@app.task(bind=True)
def debug_task(self, *args, **kwargs):
    print('Request: {0!r}'.format(self.request))


@app.task
def test_job():
    import random
    count = random.randint(1, 5)
    for i in range(count):
        _ = test_task.apply_async(args=[i], queue='test_task', routing_key='test_task')

    return count


@app.task(ignore_result=True, queue='test_task', routing_key='test_task')
def test_task(i):
    logger.info('test print: [{0}]'.format(i))
    print(i)


@app.task(queue='test_task', routing_key='test_task')
def add(a, b):
    return a + b


@app.task(ignore_result=True, queue='sync_xchat_msgs', routing_key='sync_xchat_msgs')
def sync_xchat_msgs(msg):
    sync.sync_xchat_msgs(msg)


@app.task(ignore_result=True, queue='sync_xchat_msgs', routing_key='sync_xchat_msgs')
def try_sync_proj_xchat_msgs(proj_xchat_id, xchat_msg=None):
    sync.try_sync_proj_xchat_msgs(proj_xchat_id, xchat_msg=xchat_msg)


@app.task(ignore_result=True, queue='notify_xchat_msgs', routing_key='notify_xchat_msgs')
def notify_xchat_msgs(msg):
    print('notified msg: ', msg)


# TODO: 定时扫描可能需要同步的会话
# TODO: 不同渠道之间的转发
