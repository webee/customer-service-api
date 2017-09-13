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


def project_resource(name, uselist=False):
    class ProjectResource(object):
        """属于project的资源"""
        @declared_attr
        def project_id(cls):
            return db.Column(db.BigInteger, db.ForeignKey('project.id'), index=True, nullable=False, unique=not uselist)

        @declared_attr
        def project(cls):
            kwargs = dict(uselist=uselist)
            if uselist:
                kwargs['lazy'] = 'dynamic'
            return db.relationship('Project', lazy='joined', backref=db.backref(name, **kwargs))

    return ProjectResource


def session_resource(name, uselist=False):
    class SessionResource(object):
        """属于session的资源"""
        @declared_attr
        def session_id(cls):
            return db.Column(db.BigInteger, db.ForeignKey('session.id'), index=True, nullable=False, unique=not uselist)

        @declared_attr
        def session(cls):
            kwargs = dict(uselist=uselist)
            if uselist:
                kwargs['lazy'] = 'dynamic'
            return db.relationship('Session', lazy='joined', backref=db.backref(name, **kwargs))

    return SessionResource
