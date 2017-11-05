from flask_script import Command
import celery


class Celery(Command):
    """execute celery"""

    def __init__(self, celery_app):
        self.celery_app = celery_app
        self.capture_all_args = True

    def _get_celery_app(self):
        if isinstance(self.celery_app, celery.Celery):
            return self.celery_app
        elif isinstance(self.celery_app, str):
            mod_path, app_name = map(str, self.celery_app.split(':'))
            return getattr(__import__(mod_path, fromlist=list(mod_path.split('.'))), app_name)
        else:
            raise NotImplementedError('type not supported: {0}.'.format(type(self.celery_app)))

    def run(self, *args, **kwargs):
        self._get_celery_app().start(argv=['celery'] + args[0])
