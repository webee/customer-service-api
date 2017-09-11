from app import db, dbs
from pytoolbox.util.py import classproperty
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(db.Model):
    """基本模型"""
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classproperty
    def t_query(cls):
        return dbs.session.query(cls)


def app_resource(name):
    class AppResource(object):
        """属于app的资源"""
        @declared_attr
        def app_id(cls):
            return db.Column(db.BigInteger, db.ForeignKey('app.id'), index=True, nullable=False)

        @declared_attr
        def app(cls):
            return db.relationship('App', lazy='joined', backref=db.backref(name, lazy='dynamic'))

    return AppResource
