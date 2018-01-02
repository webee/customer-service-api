import logging
from . import app
from app.biz.project import sync as proj_biz_sync
from app.biz import app as app_biz
from app.biz.app import client as app_client_biz
from app.biz import notify as notify_biz

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
    """
    根据xchat msg，同步相应的项目会话消息
    :param msg:
    :return:
    """
    proj_biz_sync.sync_xchat_msgs(msg)


@app.task(ignore_result=True, queue='sync_xchat_msgs', routing_key='sync_xchat_msgs')
def try_sync_proj_xchat_msgs(proj_id=None, proj_xchat_id=None, xchat_msg=None):
    """
    根据指定的project和提供的xchat msg，同步相应的会话消息
    :param proj_id:
    :param proj_xchat_id:
    :param xchat_msg:
    :return:
    """
    proj_biz_sync.try_sync_proj_xchat_msgs(proj_id=proj_id, proj_xchat_id=proj_xchat_id, xchat_msg=xchat_msg)


@app.task(ignore_result=True, queue='notify_xchat_msgs', routing_key='notify_xchat_msgs')
def notify_xchat_msgs(msg):
    """
    处理来自xchat的会话通知消息
    :param msg:
    :return:
    """
    print('notified msg: ', msg)


# TODO: 定时扫描可能需要同步的会话
# TODO: 不同渠道之间的转发


# sync user statuses
@app.task(ignore_result=True, queue='sync_user_statuses', routing_key='sync_user_statuses')
def sync_user_statuses(user_statuses):
    """
    同步用户的上、下线状态
    :param user_statuses:
    :return:
    """
    app_biz.sync_user_statuses(user_statuses)


# notify client
@app.task(ignore_result=True, queue='notify_client', routing_key='notify_client')
def notify_client(user, ns, type, details, domain=''):
    """
    通知客服客户端事件
    :param user:
    :param ns:
    :param type:
    :param details:
    :param domain:
    :return:
    """
    notify_biz.notify_client(user, ns, type, details, domain=domain)


# send channel msg
@app.task(ignore_result=True, queue='send_channel_msg', routing_key='send_channel_msg')
def send_channel_msgs(msgs):
    for msg in msgs:
        print('xxxxxxxxx: ', msg)
        send_channel_msg.delay(*msg)


@app.task(ignore_result=True, queue='send_channel_msg', routing_key='send_channel_msg',
          autoretry_for=(ConnectionError,), retry_kwargs={'max_retries': 3}, retry_backoff=True, retry_jitter=True,
          retry_backoff_max=600)
def send_channel_msg(app_name, channel, uid, staff, type, content, project_info):
    app_client_biz.send_channel_msg(app_name, channel, uid, staff, type, content, project_info)
