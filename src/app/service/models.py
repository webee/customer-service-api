import enum
from sqlalchemy import desc
from app import db, dbs, bcrypt
from .model_commons import BaseModel, app_resource, project_resource, session_resource, app_user
from . import constant


class UserType(enum.Enum):
    """用户类型"""
    customer = 'customer'
    staff = 'staff'
    app = 'app'


class MessageChannel(enum.Enum):
    """消息通道, 表示消息的来源"""
    # 客服系统
    cs = 'cs'
    # xchat
    xchat = 'xchat'
    # 微信
    weixin = 'weixin'
    # 电子邮件
    email = 'email'


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

    def create_or_update_customer(self, data):
        uid = data.get('uid')
        name = data.get('name')
        return self.create_customer(uid, name)

    @dbs.transactional
    def create_or_update_customers(self, customers_data):
        return [self.create_or_update_customer(customer) for customer in customers_data]

    def create_or_update_staff(self, data):
        uid = data.get('uid')
        name = data.get('name')
        return self.create_staff(uid, name)

    @dbs.transactional
    def create_or_update_staffs(self, staffs_data):
        return [self.create_or_update_staff(staff) for staff in staffs_data]

    @dbs.transactional
    def create_project_domain(self, name, title, desc):
        project_domain = ProjectDomain(app=self, name=name, title=title, desc=desc)
        db.session.add(project_domain)
        return project_domain


class Customer(BaseModel, app_user(UserType.customer.value, 'customers')):
    """客户"""
    def __repr__(self):
        return "<Customer: {}>".format(self.uid)


class Staff(BaseModel, app_user(UserType.staff.value, 'staffs')):
    """客服"""
    def __repr__(self):
        return "<Staff: {}>".format(self.uid)

    @property
    def handling_sessions(self):
        return self.as_handler_sessions.filter_by(is_active=True).order_by(desc(Session.updated))


class ProjectDomain(BaseModel, app_resource('project_domains')):
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


class ProjectType(BaseModel, app_resource('project_types')):
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


class Project(BaseModel, app_resource('projects')):
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

    # 会话
    current_session_id = db.Column(db.BigInteger, db.ForeignKey('session.id'), nullable=True)
    current_session = db.relationship('Session', foreign_keys=current_session_id, lazy='joined', post_update=True)
    # 消息id
    msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    @property
    def app_biz_id(self):
        return '%s:%s' % (self.type.app_biz_id, self.biz_id)

    @property
    def xchat_biz_id(self):
        return '%s:%s' % (constant.XCHAT_DOMAIN, self.app_biz_id)

    def __repr__(self):
        return "<Project: {}>".format(self.app_biz_id)

    # biz
    @dbs.transactional
    def create_customers(self, data):
        pc = ProjectCustomers(project=self, parties=self.app.create_or_update_customers(data['parties']))
        dbs.session.add(pc)

        return pc

    @dbs.transactional
    def create_staffs(self, data):
        leader = self.app.create_or_update_staff(data['leader'])
        assistants = self.app.create_or_update_staffs(data['assistants'])
        participants = self.app.create_or_update_staffs(data['participants'])
        ps = ProjectStaffs(project=self, leader=leader, assistants=assistants, participants=participants)
        dbs.session.add(ps)

        return ps

    @dbs.transactional
    def create_xchat(self, chat_id):
        xchat = ProjectXChat(project=self, chat_id=chat_id)
        dbs.session.add(xchat)

        return xchat

    @dbs.transactional
    def new_session(self):
        if self.current_session is None:
            self.current_session = Session(project=self, handler=self.staffs.leader)
            dbs.session.add(self)

        return self.current_session

    @dbs.transactional
    def next_msg_id(self):
        if self.current_session is None:
            self.new_session()

        self.msg_id = Project.msg_id + 1
        dbs.session.add(self)
        dbs.session.flush()

        self.current_session.msg_id = self.msg_id
        dbs.session.add(self.current_session)

        return self.msg_id

    @dbs.transactional
    def close_current_session(self):
        if self.current_session:
            self.current_session.close()


class ProjectXChat(BaseModel, project_resource('xchat', backref_lazy='joined')):
    __tablename__ = 'project_xchat'

    chat_id = db.Column(db.String(32), nullable=False, unique=True)

    def __repr__(self):
        return "<ProjectXChat: {}<->{}>".format(self.project.app_biz_id, self.chat_id)

    @dbs.transactional
    def update(self, chat_id):
        self.chat_id = chat_id

        dbs.session.add(self)


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

    @dbs.transactional
    def update(self, data):
        app = self.project.app
        self.parties = app.create_or_update_customers(data['parties'])

        dbs.session.add(self)


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

    @dbs.transactional
    def update(self, data):
        app = self.project.app
        self.leader = app.create_or_update_staff(data['leader'])
        self.assistants = app.create_or_update_staffs(data['assistants'])
        self.participants = app.create_or_update_staffs(data['participants'])

        dbs.session.add(self)


class ProjectMetaData(BaseModel, project_resource('meta_data')):
    """项目元数据"""
    __tablename__ = 'project_meta_data'

    # TODO: 怎么组织数据？
    pass


class ProjectExtData(BaseModel, project_resource('ext_data')):
    """项目扩展数据"""
    __tablename__ = 'project_ext_data'

    # TODO: 怎么组织数据？
    pass


class Session(BaseModel, project_resource('sessions', backref_uselist=True)):
    """表示一个客服项目的一次会话"""
    __tablename__ = 'session'

    # 是否接待中
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    # 关闭时间
    closed = db.Column(db.DateTime(timezone=True), nullable=True, default=None)

    # 接待者
    handler_id = db.Column(db.BigInteger, db.ForeignKey('staff.id'), nullable=False)
    handler = db.relationship('Staff', lazy='joined', backref=db.backref('as_handler_sessions', lazy='dynamic'))
    # 消息id, 0表示未指向任何消息
    msg_id = db.Column(db.BigInteger, nullable=False, default=0)

    @dbs.transactional
    def close(self):
        self.is_active = False
        self.closed = db.func.current_timestamp()
        dbs.session.add(self)

        self.project.current_session_id = None
        dbs.session.add(self.project)


class Message(BaseModel, project_resource('messages', backref_uselist=True), session_resource('messages', backref_uselist=True)):
    __tablename__ = 'message'

    # 消息通道
    channel = db.Column(db.Enum(MessageChannel), default=MessageChannel.cs, nullable=False)

    # 来自xchat的消息相关
    xchat_id = db.Column(db.BigInteger, nullable=True, index=True)

    # 发送者
    user_type = db.Column(db.Enum(UserType), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('customer.id'), nullable=True)
    customer = db.relationship('Customer', lazy='joined')
    staff_id = db.Column(db.BigInteger, db.ForeignKey('staff.id'), nullable=True)
    staff = db.relationship('Staff', lazy='joined')

    @property
    def user(self):
        if self.user_type == UserType.customer:
            return self.customer
        elif self.user_type == UserType.staff:
            return self.staff

    # 消息id
    msg_id = db.Column(db.BigInteger, nullable=False, index=True)
    # 消息域和类型
    # cs: text, file, img, voice
    # qqxb: payment, result
    domain = db.Column(db.String(16), nullable=False, default='cs')
    type = db.Column(db.String(24), nullable=False)
    content = db.Column(db.Text)
    ts = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())

    def __repr__(self):
        return "<Message: {0}: {1}, {2}, {3}>".format(self.channel.value, self.msg_id, self.domain, self.type)
