from datetime import timedelta

broker_pool_limit = 4

worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 1000


beat_schedule = {
    'test_job-E30m': {
        'task': 'app.task.tasks.test_job',
        'schedule': timedelta(minutes=30),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}
