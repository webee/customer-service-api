import arrow
import enum
from app import db, dbs, config
from pytoolbox.util.py import classproperty
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


def base_model(index_created=True, index_updated=True):
    class BaseModel(db.Model):
        """基本模型"""
        __abstract__ = True

        id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
        created = db.Column(db.DateTime(timezone=True), index=index_created, default=db.func.current_timestamp())
        updated = db.Column(db.DateTime(timezone=True), index=index_updated, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())

        @classproperty
        def t_query(cls):
            return dbs.session.query(cls)

    return BaseModel


BaseModel = base_model(False, False)


def foreign_key(key, backref_uselist=False, index=True, type=db.BigInteger, nullable=False):
    return db.Column(type, db.ForeignKey(key), index=index, nullable=nullable, unique=not backref_uselist)


def relationship(rel, name, foreign_keys, backref_uselist=False, backref_lazy=None, backref_cascade=None, lazy='joined'):
    backref_kwargs = dict(uselist=backref_uselist)
    if backref_uselist:
        backref_kwargs['lazy'] = 'dynamic'
    elif backref_lazy:
        backref_kwargs['lazy'] = backref_lazy

    if backref_cascade is not None:
        backref_kwargs['cascade'] = backref_cascade
    return db.relationship(rel, lazy=lazy, foreign_keys=foreign_keys, backref=db.backref(name, **backref_kwargs))


def app_resource(name, backref_uselist=True, backref_lazy=None, backref_cascade=None, lazy='joined'):
    class AppResource(object):
        """属于app的资源"""

        @declared_attr
        def app_name(cls):
            return foreign_key('app.name', backref_uselist=backref_uselist, type=db.String(32))

        @declared_attr
        def app(cls):
            return relationship('App', name, cls.app_name, backref_uselist, backref_lazy, backref_cascade, lazy=lazy)

    return AppResource


def app_user(type, resource_name):
    class AppUser(app_resource(resource_name)):
        __tablename__ = type

        user_type = type
        uid = db.Column(db.String(32), nullable=False)
        name = db.Column(db.String(100), nullable=False, default='')
        # 是否删除
        is_deleted = db.Column(db.Boolean, default=False)

        __table_args__ = (db.UniqueConstraint('app_name', 'uid', name='uniq_app_%s' % user_type),)

        @property
        def app_uid(self):
            return '%s:%s:%s' % (self.app_name, type, self.uid)

    return AppUser


def project_resource(name, backref_uselist=False, backref_lazy=None, backref_cascade=None):
    class ProjectResource(object):
        """属于project的资源"""

        @declared_attr
        def project_id(cls):
            return foreign_key('project.id', backref_uselist=backref_uselist)

        @declared_attr
        def project(cls):
            return relationship('Project', name, cls.project_id, backref_uselist, backref_lazy, backref_cascade)

    return ProjectResource


def session_resource(name, backref_uselist=False, backref_lazy=None, backref_cascade=None, nullable=False):
    class SessionResource(object):
        """属于session的资源"""

        @declared_attr
        def session_id(cls):
            return foreign_key('session.id', backref_uselist=backref_uselist, nullable=nullable)

        @declared_attr
        def session(cls):
            return relationship('Session', name, cls.session_id, backref_uselist, backref_lazy, backref_cascade)

    return SessionResource


class WithOnlineModel(object):
    # TODO:
    # 是否在线
    # TODO: Project是否在线, 相关的customers上线时更新这里：只要有一个在线则在线，所有都不在线才不在线
    online = db.Column(db.Boolean, default=False)
    # 上次在线通知时间
    last_online_ts = db.Column(db.DateTime(timezone=True), nullable=True, default=None)

    @dbs.transactional
    def update_online(self, online, offline_check=True):
        if not online and self.online and offline_check:
            if self.last_online_ts and arrow.utcnow() - arrow.get(self.last_online_ts) > config.Biz.USER_OFFLINE_DELTA:
                # offline check
                self.online = False
        else:
            self.online = online
            if online:
                self.last_online_ts = db.func.current_timestamp()
        db.session.add(self)

    @hybrid_property
    def is_online(self):
        return self.online and self.last_online_ts is not None and (
        self.last_online_ts > arrow.utcnow().datetime - config.Biz.USER_ONLINE_DELTA)

    @is_online.expression
    def is_online(self):
        return self.online & (self.last_online_ts != None) & (
        self.last_online_ts > arrow.utcnow().datetime - config.Biz.USER_ONLINE_DELTA)
