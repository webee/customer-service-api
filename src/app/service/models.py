from sqlalchemy import desc, orm
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import deferred
from sqlalchemy import text
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import expression
from sqlalchemy import types
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator, ExprComparator
from app import db, dbs, bcrypt, config
from app.utils.commons import merge_to_dict
from .model_commons import base_model, app_resource, project_resource, session_resource, app_user
from .model_commons import WithOnlineModel
from .utils import normalize_label_tree, normalize_labels, normalize_context_labels, normalize_data
from .utils import ignore_none

WIDEST_SCOPE_LABEL = ['all', '']
HIGHEST_CONTEXT_LABEL = ['self', '']
DEFAULT_LABELS = text("ARRAY[[NULL,NULL]]")


class UserType:
    """用户类型"""
    customer = 'customer'
    staff = 'staff'
    app = 'app'


class App(base_model()):
    """系统应用"""
    __tablename__ = 'app'

    name = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    desc = db.Column(db.String(64), nullable=False)
    # [{name, title, desc, types:[{name, title, desc}]}]
    project_domains = deferred(db.Column(db.JSON, nullable=False, default=[]))

    # 应用分配给客服系统的id和key，作为以后通信的认证元信息
    appid = deferred(db.Column(db.String(64), nullable=True, default=None), group='configs')
    appkey = deferred(db.Column(db.String(128), nullable=True, default=None), group='configs')

    # 应用提供的接口urls
    urls = deferred(db.Column(pg.HSTORE, nullable=False, default={}), group='configs')

    # 应用提供的访问功能列表
    access_functions = deferred(db.Column(db.JSON, nullable=False, default=[]))

    # 应用的客服标签树
    staff_label_tree = deferred(db.Column(db.JSON, nullable=False, default={}))

    # 应用配置信息
    configs = deferred(db.Column(db.JSON, nullable=False, default={}))

    @property
    def project_domain_type_tree(self):
        project_domains = self.project_domains
        return {domain['name']: merge_to_dict(domain, types={type['name']: type for type in domain.get('types', [])})
                for domain in project_domains}

    def __repr__(self):
        return "<App: {}>".format(self.name)

    @staticmethod
    def authenticate(name, password):
        try:
            app = App.query.filter_by(name=name).one_or_none()
            if app and bcrypt.check_password_hash(app.password, password):
                return app
        except:
            return None

    @staticmethod
    def update_app(id, values):
        App.query.filter_by(id=id).update(values)

    @dbs.transactional
    def update_password(self, new_password):
        self.password = bcrypt.generate_password_hash(new_password, rounds=9).decode()
        db.session.add(self)

    def change_password(self, password, new_password):
        if bcrypt.check_password_hash(self.password, password):
            self.update_password(new_password)
            return True

    # biz
    @ignore_none
    @dbs.transactional
    def update_urls(self, urls):
        self.urls = urls
        flag_modified(self, 'urls')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_access_functions(self, functions):
        self.access_functions = functions
        flag_modified(self, 'access_functions')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_staff_label_tree(self, tree):
        # App.update_app(self.id, dict(staff_label_tree=normalize_label_tree(tree)))
        self.staff_label_tree = normalize_label_tree(tree)
        flag_modified(self, 'staff_label_tree')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_configs(self, configs):
        self.configs = configs
        flag_modified(self, 'configs')
        db.session.add(self)

    @dbs.transactional
    def create_customer(self, uid, name=None, mobile=None, meta_data=None):
        customer = self.customers.filter_by(uid=uid).one_or_none()
        if customer is None:
            customer = Customer(app_name=self.name, app=self, uid=uid)
        elif customer.is_deleted:
            customer.is_deleted = False
        if name is not None:
            customer.name = name
        if mobile is not None:
            customer.mobile = mobile
        customer.update_meta_data(meta_data)
        db.session.add(customer)

        return customer

    @dbs.transactional
    def create_staff(self, uid, name=None, context_labels=None):
        staff = self.staffs.filter_by(uid=uid).one_or_none()
        if staff is None:
            staff = Staff(app_name=self.name, app=self, uid=uid)
        elif staff.is_deleted:
            staff.is_deleted = False
        if name is not None:
            staff.name = name
        staff.update_context_labels(context_labels)
        db.session.add(staff)

        return staff

    @dbs.transactional
    def create_project_domain_type(self, domain, type, access_functions=None, class_label_tree=None):
        project_domain_type = self.project_domain_types.filter_by(domain=domain, type=type).one_or_none()
        if project_domain_type is None:
            project_domain_type = ProjectDomainType(app=self, domain=domain, type=type)
        project_domain_type.update_access_functions(access_functions)
        project_domain_type.update_class_label_tree(class_label_tree)
        db.session.add(project_domain_type)
        return project_domain_type


class ProjectDomainType(base_model(), app_resource('project_domain_types', backref_cascade="all, delete-orphan")):
    """项目类型"""
    __tablename__ = 'project_domain_type'

    # 域
    domain = db.Column(db.String(32), nullable=False)
    # 类型
    type = db.Column(db.String(32), nullable=False)

    # 项目类型提供的访问功能列表
    access_functions = deferred(db.Column(db.JSON, nullable=False, default=[]), group='configs')
    # 项目类型的分类标签树
    class_label_tree = db.Column(db.JSON, nullable=False, default={})

    # 每个域下面类型唯一
    __table_args__ = (db.UniqueConstraint('app_name', 'domain', 'type', name='uniq_app_project_domain_type'),)

    @property
    def app_biz_id(self):
        return '%s:%s:%s' % (self.app_name, self.domain, self.type)

    # biz
    @ignore_none
    @dbs.transactional
    def update_access_functions(self, functions):
        self.access_functions = functions
        flag_modified(self, 'access_functions')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_class_label_tree(self, tree):
        self.class_label_tree = normalize_label_tree(tree)
        flag_modified(self, 'class_label_tree')
        db.session.add(self)

    def __repr__(self):
        return "<ProjectDomainType: {}>".format(self.app_biz_id)


class Customer(base_model(False, False), app_user(UserType.customer, 'customers'), WithOnlineModel):
    """客户"""
    mobile = db.Column(db.String(16), nullable=False, default="")
    # 元数据
    # [{type, value, label}, ...]
    meta_data = db.Column(db.JSON, nullable=False, default=[])

    def __repr__(self):
        return "<Customer: {}>".format(self.uid)

    # biz
    @ignore_none
    @dbs.transactional
    def update_meta_data(self, data):
        self.meta_data = normalize_data(data) or []
        flag_modified(self, 'meta_data')
        db.session.add(self)


class Staff(base_model(), app_user(UserType.staff, 'staffs'), WithOnlineModel):
    """客服"""
    # 客服定位标签
    # [{type, path}, ...]
    context_labels = db.Column(db.ARRAY(db.Text, dimensions=2), nullable=False, default=DEFAULT_LABELS)

    def __repr__(self):
        return "<Staff: {}>".format(self.uid)

    @property
    def handling_sessions(self):
        return self.as_handler_sessions.filter_by(is_active=True).options(
            orm.defaultload('project').undefer_group('data'))

    def get_handling_session(self, session_id):
        return self.as_handler_sessions.filter_by(is_active=True, id=session_id).one_or_none()

    # biz
    @ignore_none
    @dbs.transactional
    def update_context_labels(self, context_labels):
        self.context_labels = normalize_context_labels(context_labels) or DEFAULT_LABELS
        flag_modified(self, 'context_labels')
        db.session.add(self)


# many to many helpers
# # 项目客户
project_customers = db.Table('project_customers',
                             db.Column('customer_id', db.Integer, db.ForeignKey('customer.id')),
                             db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
                             )


class Project(base_model(), app_resource('projects', lazy='select'), WithOnlineModel):
    """表示一个客服项目"""
    __tablename__ = 'project'

    # 域
    domain = db.Column(db.String(32), nullable=False)
    # 类型
    type = db.Column(db.String(32), nullable=False)
    # 业务id
    biz_id = db.Column(db.String(32), nullable=False)

    # 项目tags
    tags = db.Column(db.ARRAY(db.Text), nullable=False, default=[])
    # 项目范围标签
    scope_labels = deferred(
        db.Column(db.ARRAY(db.Text, dimensions=2), nullable=False, default=DEFAULT_LABELS))
    # 项目分类标签
    class_labels = deferred(
        db.Column(db.ARRAY(db.Text, dimensions=2), nullable=False, default=DEFAULT_LABELS))

    # 元数据
    # [{type, value, label}, ...]
    meta_data = deferred(db.Column(db.JSON, nullable=False, default=[]), group='data')
    # 扩展数据
    # [{type, value, label}, ...]
    ext_data = deferred(db.Column(db.JSON, nullable=False, default=[]), group='data')
    ext_data_updated = db.Column(db.DateTime(timezone=True), nullable=True)

    # 所属客户
    owner_id = db.Column(db.BigInteger, db.ForeignKey('customer.id'), nullable=False)
    owner = db.relationship('Customer', lazy='joined', backref=db.backref('as_owner_projects', lazy='dynamic'))

    # 负责人
    leader_id = db.Column(db.BigInteger, db.ForeignKey('staff.id'), nullable=False)
    leader = db.relationship('Staff', lazy='joined', backref=db.backref('as_leader_projects', lazy='dynamic'))

    # 当事人
    customers = db.relationship('Customer', secondary=project_customers, lazy='joined', order_by="Customer.id",
                                backref=db.backref('as_customer_projects', lazy='dynamic'))

    # 上一次会话
    last_session_id = db.Column(db.BigInteger, db.ForeignKey('session.id', name='fk_project_last_session_id'),
                                nullable=True)
    last_session = db.relationship('Session', foreign_keys=last_session_id, lazy='select', post_update=True)
    # 当前会话
    current_session_id = db.Column(db.BigInteger, db.ForeignKey('session.id', name='fk_project_current_session_id'),
                                   nullable=True)
    current_session = db.relationship('Session', foreign_keys=current_session_id, lazy='select', post_update=True)
    # 起始消息id
    # TODO: 迁移消息和发送消息一样，先发送到xchat，再同步到cs
    start_msg_id = db.Column(db.BigInteger, nullable=False, default=0)
    # 消息id
    msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    # 每个项目类型的业务id唯一
    __table_args__ = (
        db.UniqueConstraint('app_name', 'domain', 'type', 'biz_id', name='uniq_app_project_domain_type_biz'),)

    @property
    def app_biz_id(self):
        return '%s:%s:%s:%s' % (self.app_name, self.domain, self.type, self.biz_id)

    @property
    def xchat_biz_id(self):
        return '%s:%s' % (config.App.NAME, self.app_biz_id)

    def __repr__(self):
        return "<Project: {}>".format(self.app_biz_id)

    # biz
    @dbs.transactional
    def create_or_update_xchat(self, chat_id, start_msg_id):
        if self.xchat:
            assert chat_id == self.xchat.chat_id, 'chat_id should not change'
            return self.xchat
        else:
            xchat = ProjectXChat(project=self, chat_id=chat_id, start_msg_id=start_msg_id, msg_id=start_msg_id)
            db.session.add(xchat)
            return xchat

    @ignore_none
    @dbs.transactional
    def update_tags(self, tags):
        self.tags = tags or []
        flag_modified(self, 'tags')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_scope_labels(self, labels):
        self.scope_labels = normalize_labels(labels) or DEFAULT_LABELS
        flag_modified(self, 'scope_labels')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_class_labels(self, labels):
        self.class_labels = normalize_labels(labels) or DEFAULT_LABELS
        flag_modified(self, 'class_labels')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_meta_data(self, data):
        self.meta_data = normalize_data(data) or []
        flag_modified(self, 'meta_data')
        db.session.add(self)

    @ignore_none
    @dbs.transactional
    def update_ext_data(self, data):
        self.ext_data = normalize_data(data) or []
        self.ext_data_updated = db.func.current_timestamp()
        flag_modified(self, 'ext_data')
        db.session.add(self)


class ProjectXChat(base_model(), project_resource('xchat')):
    __tablename__ = 'project_xchat'

    chat_id = db.Column(db.String(32), nullable=False, unique=True)
    # 同步消息范围start_msg_id < x <= msg_id
    # 起始消息id, 不包含在已同步消息中
    start_msg_id = db.Column(db.BigInteger, nullable=False, default=0)
    # 已接收最大消息id, 默认=start_msg_id
    msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    # 同步控制
    # init: *, False
    # running: 0, True
    # running_with_pending: >0, True
    # # 有同步需求
    pending = db.Column(db.Integer, nullable=False, default=0)
    # # 正在同步
    syncing = db.Column(db.Boolean, nullable=False, default=False)

    migrate_pending = db.Column(db.Integer, nullable=False, default=0)
    migrate_syncing = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<ProjectXChat: {}<->{}>".format(self.project.app_biz_id, self.chat_id)

    @staticmethod
    def get_pending(syncing='syncing'):
        if syncing == 'migrate_syncing':
            return ProjectXChat.migrate_pending
        return ProjectXChat.pending

    @staticmethod
    @dbs.transactional
    def try_sync(id, syncing='syncing'):
        """尝试同步"""
        # init -> running
        if ProjectXChat.query.filter_by(id=id, **{syncing: False}).update({syncing: True}):
            return True
        # running/running_with_pending -> running_with_pending
        pending = ProjectXChat.get_pending(syncing)
        ProjectXChat.query.filter_by(id=id, **{syncing: True}).update({pending: pending + 1})
        return False

    @staticmethod
    def current_pending(id, syncing='syncing'):
        """当前pending"""
        pending = ProjectXChat.get_pending(syncing)
        return db.session.query(pending).filter_by(id=id).one()[0]

    @staticmethod
    @dbs.transactional
    def done_sync(id, cur_pending=0, syncing='syncing'):
        """完成同步"""
        pending = ProjectXChat.get_pending(syncing)
        # running_with_pending -> running
        ProjectXChat.query.filter_by(id=id, **{syncing: True}).filter(pending > 0) \
            .update({pending: pending - cur_pending})
        # running -> init
        return ProjectXChat.query.filter_by(id=id, **{syncing: True}).filter(pending == 0).update({syncing: False})

    @staticmethod
    @dbs.transactional
    def stop_sync(id, syncing='syncing'):
        """结束同步"""
        # running -> init
        return ProjectXChat.query.filter_by(id=id, **{syncing: True}).update({syncing: False})


class Session(base_model(), project_resource('sessions', backref_uselist=True)):
    """表示一个客服项目的一次会话"""
    __tablename__ = 'session'

    # TODO: 添加tags管理, 客服自定义tags和app定义tags
    # tags

    # 是否接待中
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    # 会话状态：可以用来标识接待进度及分类管理
    # TODO: 添加状态管理, 客服自定义tags和app定义tags
    # status = db.Column(db.String(12), nullable=True, default=None, index=True)
    # 关闭时间
    closed = db.Column(db.DateTime(timezone=True), nullable=True, default=None)

    # 接待者
    handler_id = db.Column(db.BigInteger, db.ForeignKey('staff.id'), nullable=False)
    handler = db.relationship('Staff', lazy='joined', backref=db.backref('as_handler_sessions', lazy='dynamic'))

    # 起始消息id, 不属于当前会话
    start_msg_id = db.Column(db.BigInteger, nullable=False)
    # 消息id, 0表示未指向任何消息
    msg_id = db.Column(db.BigInteger, nullable=False, default=0)
    msg = db.relationship('Message', uselist=False,
                          primaryjoin="and_(Session.id == Message.session_id, Session.msg_id == Message.msg_id)",
                          lazy='joined')

    # 处理者消息id, 0表示未指向任何消息
    handler_msg_id = db.Column(db.BigInteger, nullable=False, default=0)
    handler_msg = db.relationship('Message', uselist=False,
                                  primaryjoin="and_(Session.id == Message.session_id, Session.handler_msg_id == Message.msg_id)")

    # 已经同步的消息id(已读id)
    sync_msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    # 当前激活的其它通道
    activated_channel = db.Column(db.String(16), nullable=True, default=None)
    channel_user_id = db.Column(db.String(32), nullable=True, default=None)

    def __repr__(self):
        return "<Session: {0}, {1}, {2}/{3}/{4}>".format(self.project.app_biz_id,
                                                         'active' if self.is_active else 'closed', self.unsynced_count,
                                                         self.unhandled_count, self.msg_count)

    @property
    def last_session_msg(self):
        """本次会话的最后一条消息"""
        if self.msg_id > self.start_msg_id:
            return self.msg

    @hybrid_property
    def msg_count(self):
        if self.msg_id == 0:
            return 0
        return self.msg_id - self.start_msg_id

    @hybrid_property
    def unsynced_count(self):
        if self.msg_id == 0:
            return 0
        elif self.sync_msg_id == 0:
            return self.msg_id - self.start_msg_id
        return self.msg_id - self.sync_msg_id

    @hybrid_property
    def unhandled_count(self):
        if self.msg_id == 0:
            return 0
        elif self.handler_msg_id == 0:
            return self.msg_id - self.start_msg_id
        return self.msg_id - self.handler_msg_id

    @msg_count.expression
    def msg_count(self):
        return expression.case([(self.msg_id == 0, 0)], else_=self.msg_id - self.start_msg_id)

    @unsynced_count.expression
    def unsynced_count(self):
        return expression.case([(self.msg_id == 0, 0),
                                (self.sync_msg_id == 0, self.msg_id - self.start_msg_id)],
                               else_=self.msg_id - self.sync_msg_id)

    @unhandled_count.expression
    def unhandled_count(self):
        return expression.case([(self.msg_id == 0, 0),
                                (self.handler_msg_id == 0, self.msg_id - self.start_msg_id)],
                               else_=self.msg_id - self.handler_msg_id)


class Message(base_model(False, False), project_resource('messages', backref_uselist=True),
              session_resource('messages', backref_uselist=True, nullable=True)):
    __tablename__ = 'message'

    # 消息通道: 除了来自客服系统自身和xchat的其它通道
    channel = db.Column(db.String(16), nullable=True, default=None)

    # 发送者
    user_type = db.Column(db.String(12), nullable=True)
    user_id = db.Column(db.String(32), nullable=True)

    # tx key: 客户端发送的，用于防止重复发送
    tx_key = db.Column(db.BigInteger, nullable=True)
    # rx key: 服务端返回的，用于异步处理消息发送时给客户端的一个临时唯一消息id, 用于乐观展示
    #           目前为xchat_chat_id
    rx_key = db.Column(db.BigInteger, nullable=True)

    # 消息id
    msg_id = db.Column(db.BigInteger, nullable=False, index=True)
    # 消息域和类型(类型只能为小写字母)
    # '': '', text, file, image, voice, xxx
    # qqxb: payment, result
    domain = db.Column(db.String(16), nullable=False, default='')
    type = db.Column(db.String(24), nullable=False, default='')
    content = db.Column(db.Text)
    # 消息的状态, isTerminal=true
    state = db.Column(db.JSON, nullable=True)

    # 消息发生的时间，以来源通道为准，
    # msg_id和updated总是递增的，但由于不同渠道同步消息的延迟, 因此可能会出现ts不递增的情况
    ts = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())

    # project_id, msg_id唯一
    __table_args__ = (db.UniqueConstraint('project_id', 'msg_id', name='uniq_project_msg_id'),
                      db.Index('idx_message_domain_type', "domain", "type"))

    @ignore_none
    @dbs.transactional
    def update_state(self, state):
        self.state = state
        flag_modified(self, 'state')
        db.session.add(self)

    def __repr__(self):
        return "<Message: {0}, [{1}, {2}, {3}]>".format(self.channel, self.msg_id, self.domain, self.type)
