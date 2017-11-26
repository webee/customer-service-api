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


task_default_queue = 'celery'
task_queues = (
    Queue('celery', Exchange('celery', 'direct'), routing_key='celery'),
    Queue('celery_periodic', Exchange('celery_periodic', 'direct'), routing_key='celery_periodic'),
    Queue('test_task', Exchange('test_task', 'direct'), routing_key='test_task'),
    Queue('sync_xchat_msgs', Exchange('sync_xchat_msgs', 'direct'), routing_key='sync_xchat_msgs'),
    Queue('notify_xchat_msgs', Exchange('notify_xchat_msgs', 'direct'), routing_key='notify_xchat_msgs'),
    Queue('sync_user_statuses', Exchange('sync_user_statuses', 'direct'), routing_key='sync_user_statuses'),
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
