from app import db, dbs
from .models import App


@dbs.transactional
def create_app(name, password, title, desc):
    app = App(name=name, password=password, title=title, desc=desc)
    db.session.add(app)

    return app
