from app import db
from app.service.models import App
from app.utils import dbs


@dbs.transactional
def create_app(name, password, title, desc):
    app = App(name=name, password=password, title=title, desc=desc)
    db.session.add(app)

    return app
