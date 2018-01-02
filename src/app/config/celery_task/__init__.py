from kombu import Queue, Exchange
from datetime import timedelta


broker_url = 'redis://127.0.0.1:6379/13'
result_backend = 'rpc://'
result_serializer = 'pickle'
accept_content = ['json', 'pickle']
result_persistent = False

broker_pool_limit = 16

worker_prefetch_multiplier = 8
worker_max_tasks_per_child = 1000


# fixme
redis_socket_connect_timeout = 8
redis_socket_timeout = 15
broker_connection_timeout = 8


task_default_queue = 'celery'
task_queues = (
    Queue('celery', Exchange('celery', 'direct'), routing_key='celery'),
    Queue('celery_periodic', Exchange('celery_periodic', 'direct'), routing_key='celery_periodic'),
    Queue('test_task', Exchange('test_task', 'direct'), routing_key='test_task'),
    Queue('sync_xchat_msgs', Exchange('sync_xchat_msgs', 'direct'), routing_key='sync_xchat_msgs'),
    Queue('notify_xchat_msgs', Exchange('notify_xchat_msgs', 'direct'), routing_key='notify_xchat_msgs'),
    Queue('sync_user_statuses', Exchange('sync_user_statuses', 'direct'), routing_key='sync_user_statuses'),
    Queue('notify_client', Exchange('notify_client', 'direct'), routing_key='notify_client'),
    Queue('send_channel_msg', Exchange('send_channel_msg', 'direct'), routing_key='send_channel_msg'),
)

task_routes = {
    'app.task.tasks.test_task': {'queue': 'test_task', 'routing_key': 'test_task'},
}


beat_schedule = {
    'test_job-E0.5d': {
        'task': 'app.task.tasks.test_job',
        'schedule': timedelta(days=0.5),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}

timezone = 'UTC'
