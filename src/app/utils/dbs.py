from contextlib import contextmanager
from functools import wraps


db = None
session = None


def init_app(app, _db):
    global db, session
    db = _db
    session = _db.session


@contextmanager
def require_transaction_context():
    is_entry = not hasattr(db.session, '__nested')
    try:
        if is_entry:
            # 因为是自动开始事务，所以第一层可以不开始嵌套事务
            setattr(db.session, '__nested', 0)
            yield
            db.session.commit()
        else:
            with db.session.begin_nested():
                db.session.__nested += 1
                yield
    except:
        if is_entry:
            db.session.rollback()
        raise
    finally:
        if is_entry:
            delattr(db.session, '__nested')


def transactional(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with require_transaction_context():
            return func(*args, **kwargs)

    return wrapper
