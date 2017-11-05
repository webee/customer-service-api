from celery import Celery

app = Celery('app')


def init_celery_app(app: Celery, config, flask_app=None):
    app.config_from_object(config)

    if flask_app is not None:
        BaseTask = app.Task

        class ContextTask(BaseTask):
            abstract = True

            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return BaseTask.__call__(self, *args, **kwargs)

        app.Task = ContextTask

    return app
