from app import db
from .models import App


def create_app(name, password, desc):
    app = App(name=name, password=password, desc=desc)
    db.session.add(app)
    db.session.commit()

    return app
