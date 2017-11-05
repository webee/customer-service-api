from datetime import timedelta


beat_schedule = {
    'test_job-E30s': {
        'task': 'app.task.tasks.test_job',
        'schedule': timedelta(seconds=30),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}
