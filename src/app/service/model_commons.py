from app import db, dbs
from app.utils.py import classproperty


class BaseModel(db.Model):
    """基本模型"""
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classproperty
    def t_query(cls):
        return dbs.session.query(cls)


