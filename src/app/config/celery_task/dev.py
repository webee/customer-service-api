from datetime import timedelta


beat_schedule = {
    'test_job-E30m': {
        'task': 'app.task.tasks.test_job',
        'schedule': timedelta(minutes=30),
        'kwargs': {},
        'relative': True,
        'options': {'queue': 'celery_periodic'}
    },
}
