from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager
from functools import wraps


db = SQLAlchemy(session_options={'autocommit': True})
session = db.session


def init_app(app):
    db.init_app(app)


@contextmanager
def require_transaction_context():
    with db.session.begin(subtransactions=True, nested=False):
        yield db
        db.session.flush()


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with require_transaction_context() as _:
            return func(*args, **kwargs)

    return wrapper
