from datetime import timedelta


broker_url = 'redis://127.0.0.1:6379/8'

broker_pool_limit = 4

worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 1000

beat_schedule = {
    'test_job-E1h': {
        'task': 'app.task.tasks.test_job',
        'schedule': timedelta(hours=1),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}
