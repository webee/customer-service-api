from app import db, dbs
from pytoolbox.util.py import classproperty
from sqlalchemy.ext.declarative import declared_attr


class BaseModel(db.Model):
    """基本模型"""
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    updated = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classproperty
    def t_query(cls):
        return dbs.session.query(cls)


def foreign_key(key, backref_uselist=False, index=True):
    return db.Column(db.BigInteger, db.ForeignKey(key), index=index, nullable=False, unique=not backref_uselist)


def relationship(rel, name, foreign_keys, backref_uselist=False, backref_lazy=None):
    backref_kwargs = dict(uselist=backref_uselist)
    if backref_uselist:
        backref_kwargs['lazy'] = 'dynamic'
    elif backref_lazy:
        backref_kwargs['lazy'] = backref_lazy
    return db.relationship(rel, lazy='joined', foreign_keys=foreign_keys, backref=db.backref(name, **backref_kwargs))


def app_resource(name, backref_uselist=True, backref_lazy=None):
    class AppResource(object):
        """属于app的资源"""
        @declared_attr
        def app_id(cls):
            return foreign_key('app.id', backref_uselist=backref_uselist)

        @declared_attr
        def app(cls):
            return relationship('App', name, cls.app_id, backref_uselist, backref_lazy)

    return AppResource


def app_user(user_type, resource_name):
    class AppUser(app_resource(resource_name)):
        __tablename__ = user_type

        uid = db.Column(db.String(32), nullable=False)
        name = db.Column(db.String(16), nullable=False)

        __table_args__ = (db.UniqueConstraint('app_id', 'uid', name='uniq_app_%s' % user_type),)

        @property
        def app_uid(self):
            return '%s:%s:%s' % (self.app.name, user_type, self.uid)

    return AppUser


def project_resource(name, backref_uselist=False, backref_lazy=None):
    class ProjectResource(object):
        """属于project的资源"""
        @declared_attr
        def project_id(cls):
            return foreign_key('project.id', backref_uselist=backref_uselist)

        @declared_attr
        def project(cls):
            return relationship('Project', name, cls.project_id, backref_uselist, backref_lazy)

    return ProjectResource


def session_resource(name, backref_uselist=False, backref_lazy=None):
    class SessionResource(object):
        """属于session的资源"""
        @declared_attr
        def session_id(cls):
            return foreign_key('session.id', backref_uselist=backref_uselist)

        @declared_attr
        def session(cls):
            return relationship('Session', name, cls.session_id, backref_uselist, backref_lazy)

    return SessionResource
