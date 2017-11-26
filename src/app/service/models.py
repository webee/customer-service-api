import json
from sqlalchemy import desc
from app import db, dbs, bcrypt
from .model_commons import BaseModel, app_resource, project_resource, session_resource, app_user
from .model_commons import WithOnlineModel
from .model_commons import GenericDataItem
from . import constant


class UserType:
    """用户类型"""
    customer = 'customer'
    staff = 'staff'
    app = 'app'


class App(BaseModel):
    """系统应用"""
    __tablename__ = 'app'

    name = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    desc = db.Column(db.String(64), nullable=False)

    def __init__(self, name, password, title, desc):
        self.name = name
        self.password = bcrypt.generate_password_hash(password).decode()
        self.title = title
        self.desc = desc

    def __repr__(self):
        return "<App: {}>".format(self.name)

    @staticmethod
    def authenticate(name, password):
        app = App.query.filter_by(name=name).one_or_none()
        if app and bcrypt.check_password_hash(app.password, password):
            return app

    def set_password(self, new_password):
        self.password = bcrypt.generate_password_hash(new_password).decode()
        db.session.add(self)
        db.session.commit()

    def change_password(self, password, new_password):
        if bcrypt.check_password_hash(self.password, password):
            self.set_password(new_password)
            return True

    @property
    def ordered_project_domains(self):
        return self.project_domains.order_by(ProjectDomain.id)

    # biz
    @dbs.transactional
    def create_customer(self, uid, name):
        customer = self.customers.filter_by(uid=uid).one_or_none()
        if customer is None:
            customer = Customer(app=self, uid=uid)
        customer.name = name or customer.name
        db.session.add(customer)

        return customer

    @dbs.transactional
    def create_staff(self, uid, name):
        staff = self.staffs.filter_by(uid=uid).one_or_none()
        if staff is None:
            staff = Staff(app=self, uid=uid)
        staff.name = name or staff.name
        dbs.session.add(staff)

        return staff

    @dbs.transactional
    def create_project_domain(self, name, title, desc):
        project_domain = ProjectDomain(app=self, name=name, title=title, desc=desc)
        db.session.add(project_domain)
        return project_domain

    @dbs.transactional
    def create_configs(self):
        configs = AppConfigs(app=self)
        dbs.session.add(configs)

        return configs


class AppConfigs(BaseModel, app_resource('configs', backref_uselist=False, backref_lazy='select')):
    __tablename__ = 'app_configs'

    # 应用分配给客服系统的id和key，作为以后通信的认证元信息
    aid = db.Column(db.String(64), nullable=True, default=None)
    akey = db.Column(db.String(128), nullable=True, default=None)

    # TODO: 使用上面的key签名，设计接口规范
    # 服务提供的接口根url
    # 接口：1、获取token；2、事件通知接口（消息转发等）；3、获取项目扩展信息等
    base_url = db.Column(db.String(256), nullable=True, default=None)

    def __repr__(self):
        return "<AppConfigs: {}>".format(self.app.name)


class Customer(BaseModel, app_user(UserType.customer, 'customers'), WithOnlineModel):
    """客户"""

    def __repr__(self):
        return "<Customer: {}>".format(self.uid)


class Staff(BaseModel, app_user(UserType.staff, 'staffs'), WithOnlineModel):
    """客服"""

    def __repr__(self):
        return "<Staff: {}>".format(self.uid)

    @property
    def handling_sessions(self):
        return self.as_handler_sessions.filter_by(is_active=True).order_by(desc(Session.msg_ts))

    def get_handling_session(self, session_id):
        return self.as_handler_sessions.filter_by(id=session_id).one_or_none()


class ProjectDomain(BaseModel, app_resource('project_domains', backref_cascade="all, delete-orphan")):
    """项目域"""
    __tablename__ = 'project_domain'

    name = db.Column(db.String(32), nullable=False, index=True)
    # eg: 个人，员工，企业
    title = db.Column(db.String(32), nullable=False)
    desc = db.Column(db.String(64), nullable=False)

    # 每个app下面域唯一
    __table_args__ = (db.UniqueConstraint('app_id', 'name', name='uniq_app_domain'),)

    @property
    def app_biz_id(self):
        return '%s:%s' % (self.app.name, self.name)

    def __repr__(self):
        return "<ProjectDomain: {}>".format(self.name)

    @property
    def ordered_types(self):
        return self.types.order_by(ProjectType.id)

    @dbs.transactional
    def create_project_type(self, name, title, desc):
        project_type = ProjectType(app=self.app, domain=self, name=name, title=title, desc=desc)
        db.session.add(project_type)
        return project_type


class ProjectType(BaseModel, app_resource('project_types', backref_cascade="all, delete-orphan")):
    """项目类型"""
    __tablename__ = 'project_type'

    domain_id = db.Column(db.BigInteger, db.ForeignKey('project_domain.id'), index=True, nullable=False)
    domain = db.relationship('ProjectDomain', lazy='joined', backref=db.backref('types', lazy='dynamic'))

    name = db.Column(db.String(32), nullable=False, index=True)
    # eg: 咨询，专业业务订单，工单
    title = db.Column(db.String(32), nullable=False)
    desc = db.Column(db.String(64), nullable=False)

    # 每个域下面类型唯一
    __table_args__ = (db.UniqueConstraint('domain_id', 'name', name='uniq_domain_type'),)

    @property
    def app_biz_id(self):
        return '%s:%s' % (self.domain.app_biz_id, self.name)

    def __repr__(self):
        return "<ProjectType: {}:{}>".format(self.domain.name, self.name)


class ProjectTypeConfigs(BaseModel):
    """项目类型配置"""
    __tablename__ = 'project_type_configs'


class Project(BaseModel, app_resource('projects'), WithOnlineModel):
    """表示一个客服项目"""
    __tablename__ = 'project'

    # 域
    domain_id = db.Column(db.BigInteger, db.ForeignKey('project_domain.id'), index=True, nullable=False)
    domain = db.relationship('ProjectDomain', lazy='joined', backref=db.backref('projects', lazy='dynamic'))
    # 类型
    type_id = db.Column(db.BigInteger, db.ForeignKey('project_type.id'), index=True, nullable=False)
    type = db.relationship('ProjectType', lazy='joined', backref=db.backref('projects', lazy='dynamic'))

    # 业务id
    biz_id = db.Column(db.String(32), nullable=False)

    # 每个项目类型的业务id唯一
    __table_args__ = (db.UniqueConstraint('type_id', 'biz_id', name='uniq_type_biz'),)

    # 所属客户
    owner_id = db.Column(db.BigInteger, db.ForeignKey('customer.id'), nullable=False)
    owner = db.relationship('Customer', lazy='joined', backref=db.backref('as_owner_projects', lazy='dynamic'))

    # 上一次会话
    last_session_id = db.Column(db.BigInteger, db.ForeignKey('session.id'), nullable=True)
    last_session = db.relationship('Session', foreign_keys=last_session_id, lazy='joined', post_update=True)
    # 当前会话
    current_session_id = db.Column(db.BigInteger, db.ForeignKey('session.id'), nullable=True)
    current_session = db.relationship('Session', foreign_keys=current_session_id, lazy='joined', post_update=True)
    # 起始消息id
    # TODO: 迁移消息各发送消息一样，先发送到xchat，再同步到cs
    start_msg_id = db.Column(db.BigInteger, nullable=False, default=0)
    # 消息id
    msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    @property
    def app_biz_id(self):
        return '%s:%s' % (self.type.app_biz_id, self.biz_id)

    @property
    def xchat_biz_id(self):
        return '%s:%s' % (constant.XCHAT_DOMAIN, self.app_biz_id)

    @property
    def ordered_meta_data(self):
        return [dict(key=item.key,
                     type=json.loads(item.type),
                     value=json.loads(item.value),
                     label=item.label) for item in self.meta_data.order_by(ProjectMetaData.index, ProjectMetaData.id)]

    @property
    def ordered_ext_data(self):
        return self.ext_data.order_by(ProjectExtData.index, ProjectExtData.id)

    def __repr__(self):
        return "<Project: {}>".format(self.app_biz_id)

    @dbs.transactional
    def create_xchat(self, chat_id):
        xchat = ProjectXChat(project=self, chat_id=chat_id)
        dbs.session.add(xchat)

        return xchat

    @dbs.transactional
    def create_meta_data_item(self, key, type, value, label, index):
        meta_data_item = self.meta_data.filter_by(key=key).one_or_none()
        if meta_data_item is None:
            meta_data_item = ProjectMetaData(project=self, key=key)
        meta_data_item.type = type or meta_data_item.type
        meta_data_item.value = value or meta_data_item.value
        meta_data_item.label = label or meta_data_item.lable
        meta_data_item.index = index or meta_data_item.index

        dbs.session.add(meta_data_item)

        return meta_data_item


class ProjectXChat(BaseModel, project_resource('xchat', backref_lazy='joined')):
    __tablename__ = 'project_xchat'

    chat_id = db.Column(db.String(32), nullable=False, unique=True)
    # 起始消息id
    start_msg_id = db.Column(db.BigInteger, nullable=False, default=0)
    # 已接收最大消息id
    msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    # 同步控制
    # init: *, False
    # running: 0, True
    # running_with_pending: >0, True
    # # 有同步需求
    pending = db.Column(db.Integer, nullable=False, default=0)
    # # 正在同步
    syncing = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<ProjectXChat: {}<->{}>".format(self.project.app_biz_id, self.chat_id)

    @staticmethod
    @dbs.transactional
    def try_sync(id):
        """尝试同步"""
        # init -> running
        if ProjectXChat.query.filter_by(id=id, syncing=False).update({'syncing': True}):
            return True
        # running/running_with_pending -> running_with_pending
        ProjectXChat.query.filter_by(id=id, syncing=True).update({ProjectXChat.pending: ProjectXChat.pending + 1})
        return False

    @staticmethod
    def current_pending(id):
        """当前pending"""
        return dbs.session.query(ProjectXChat.pending).filter_by(id=id).one().pending

    @staticmethod
    @dbs.transactional
    def done_sync(id, pending=0):
        """完成同步"""
        # running_with_pending -> running
        ProjectXChat.query.filter_by(id=id, syncing=True).filter(ProjectXChat.pending > 0) \
            .update({ProjectXChat.pending: ProjectXChat.pending - pending})
        # running -> init
        return ProjectXChat.query.filter_by(id=id, syncing=True, pending=0).update({'syncing': False})

    @staticmethod
    @dbs.transactional
    def stop_sync(id):
        """结束同步"""
        # running -> init
        return ProjectXChat.query.filter_by(id=id, syncing=True).update({'syncing': False})


# many to many helpers
# # 项目客户当事人
project_customer_parties = db.Table('project_customer_parties',
                                    db.Column('customer_id', db.Integer, db.ForeignKey('customer.id')),
                                    db.Column('project_customers_id', db.Integer, db.ForeignKey('project_customers.id'))
                                    )
# # 项目客服协助人
project_staff_assistants = db.Table('project_staff_assistants',
                                    db.Column('staff_id', db.Integer, db.ForeignKey('staff.id')),
                                    db.Column('project_staffs_id', db.Integer, db.ForeignKey('project_staffs.id'))
                                    )
# # 项目客服参与人
project_staff_participants = db.Table('project_staff_participants',
                                      db.Column('staff_id', db.Integer, db.ForeignKey('staff.id')),
                                      db.Column('project_staffs_id', db.Integer, db.ForeignKey('project_staffs.id'))
                                      )


class ProjectCustomers(BaseModel, project_resource('customers')):
    """项目相关客户"""
    __tablename__ = 'project_customers'

    # 当事人
    parties = db.relationship('Customer', secondary=project_customer_parties, lazy='joined',
                              backref=db.backref('as_party_projects', lazy='dynamic'))


class ProjectStaffs(BaseModel, project_resource('staffs')):
    """项目相关客服"""
    __tablename__ = 'project_staffs'

    # 负责人
    leader_id = db.Column(db.BigInteger, db.ForeignKey('staff.id'), nullable=False)
    leader = db.relationship('Staff', lazy='joined',
                             backref=db.backref('as_leader_projects', lazy='dynamic'))
    # 协助人
    assistants = db.relationship('Staff', secondary=project_staff_assistants, lazy='joined',
                                 backref=db.backref('as_assistant_projects', lazy='dynamic'))
    # 参与人
    participants = db.relationship('Staff', secondary=project_staff_participants, lazy='joined',
                                   backref=db.backref('as_participant_projects', lazy='dynamic'))


class ProjectMetaData(BaseModel, GenericDataItem, project_resource('meta_data', backref_uselist=True, backref_cascade="all, delete-orphan")):
    """项目元数据: 作为客服界面展示的一个数据缓存"""
    __tablename__ = 'project_meta_data'

    # project_id, key唯一
    __table_args__ = (db.UniqueConstraint('project_id', 'key', name='uniq_project_meta_data_key'),)

    def __repr__(self):
        return "<ProjectMetaData: {}({})>".format(self.key, self.label)


class ProjectExtData(BaseModel, GenericDataItem, project_resource('ext_data', backref_uselist=True, backref_cascade="all, delete-orphan")):
    """项目扩展数据：作为客服界面展示的一个数据缓存"""
    __tablename__ = 'project_ext_data'

    # project_id, key唯一
    __table_args__ = (db.UniqueConstraint('project_id', 'key', name='uniq_project_ext_data_key'),)

    def __repr__(self):
        return "<ProjectExtData: {}({})>".format(self.key, self.label)


class Session(BaseModel, project_resource('sessions', backref_uselist=True)):
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
    # 消息接收的时间
    msg_ts = db.Column(db.DateTime(timezone=True), index=True, default=db.func.current_timestamp())

    # 已经同步的消息id(已读id)
    sync_msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    # 当前激活的其它通道
    activated_channel = db.Column(db.String(16), nullable=True, default=None)

    def __repr__(self):
        return "<Session: {0}, {1}, {2}>".format(self.project.app_biz_id, 'active' if self.is_active else 'closed',
                                                 self.msg_id)


class Message(BaseModel, project_resource('messages', backref_uselist=True),
              session_resource('messages', backref_uselist=True)):
    __tablename__ = 'message'

    # 消息通道: 除了来自客服系统自身和xchat的其它通道
    channel = db.Column(db.String(16), nullable=True, default=None)

    # 发送者
    user_type = db.Column(db.String(12), nullable=True)
    user_id = db.Column(db.String(32), nullable=True)

    # 消息id
    msg_id = db.Column(db.BigInteger, nullable=False, index=True)
    # 消息域和类型(类型只能为小写字母)
    # '': '', text, file, image, voice, xxx
    # qqxb: payment, result
    domain = db.Column(db.String(16), nullable=False, default='')
    type = db.Column(db.String(24), nullable=False, default='')
    content = db.Column(db.Text)

    # 消息发生的时间，以来源通道为准，
    # msg_id和updated总是递增的，但由于不同渠道同步消息的延迟, 因此可能会出现ts不递增的情况
    ts = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())

    # project_id, msg_id唯一
    __table_args__ = (db.UniqueConstraint('project_id', 'msg_id', name='uniq_project_msg_id'),)

    def __repr__(self):
        return "<Message: {0}, [{1}, {2}, {3}]>".format(self.channel, self.msg_id, self.domain, self.type)
