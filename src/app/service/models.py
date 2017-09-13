import enum
from app import db, dbs, bcrypt
from .model_commons import BaseModel, app_resource, project_resource, session_resource


class Channel(enum.Enum):
    """消息通道"""
    # cs, 由客服系统产生
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
    desc = db.Column(db.String(64), nullable=False)

    def __init__(self, name, password, desc):
        self.name = name
        self.password = bcrypt.generate_password_hash(password).decode()
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

    # biz
    @dbs.transactional
    def create_or_update_customer(self, data):
        uid = data['uid']
        name = data['name']
        customer = self.customers.filter_by(uid=uid).one_or_none()
        if customer is None:
            customer = Customer(app=self, uid=uid)
        customer.name = name
        dbs.session.add(customer)

        return customer

    @dbs.transactional
    def create_or_update_customers(self, customers_data):
        return [self.create_or_update_customer(customer) for customer in customers_data]

    @dbs.transactional
    def create_or_update_staff(self, data):
        uid = data['uid']
        name = data['name']
        staff = self.staffs.filter_by(uid=uid).one_or_none()
        if staff is None:
            staff = Staff(app=self, uid=uid)
        staff.name = name
        dbs.session.add(staff)

        return staff

    @dbs.transactional
    def create_or_update_staffs(self, staffs_data):
        return [self.create_or_update_staff(staff) for staff in staffs_data]


class Customer(BaseModel, app_resource('customers')):
    """客户"""
    __tablename__ = 'customer'

    uid = db.Column(db.String(32), nullable=False, unique=True)
    name = db.Column(db.String(16), nullable=False)

    # 每个app下面customer唯一
    __table_args__ = (db.UniqueConstraint('app_id', 'uid', name='uniq_app_customer'),)

    @property
    def ns_app_uid(self):
        return '%s:%s.%s' % ('cust', self.app.name, self.uid)

    def __repr__(self):
        return "<Customer: {}>".format(self.uid)


class Staff(BaseModel, app_resource('staffs')):
    """客服"""
    __tablename__ = 'staff'

    uid = db.Column(db.String(32), nullable=False, unique=True)
    name = db.Column(db.String(16), nullable=False)

    # 每个app下面staff唯一
    __table_args__ = (db.UniqueConstraint('app_id', 'uid', name='uniq_app_staff'),)

    @property
    def ns_app_uid(self):
        return '%s:%s.%s' % ('staff', self.app.name, self.uid)

    def __repr__(self):
        return "<Staff: {}>".format(self.uid)


class ProjectDomain(BaseModel, app_resource('project_domains')):
    """项目域"""
    __tablename__ = 'project_domain'

    app_id = db.Column(db.BigInteger, db.ForeignKey('app.id'), index=True, nullable=False)
    app = db.relationship('App', lazy='joined', backref=db.backref('project_domains', lazy='dynamic'))

    # eg: 个人，员工，企业
    name = db.Column(db.String(32), nullable=False, index=True)
    desc = db.Column(db.String(64), nullable=False)

    # 每个app下面域唯一
    __table_args__ = (db.UniqueConstraint('app_id', 'name', name='uniq_app_domain'),)

    def to_dict(self):
        return dict(name=self.name, desc=self.desc, types=[t.to_dict() for t in self.types])

    @property
    def app_biz_id(self):
        return '%s:%s' % (self.app.name, self.name)

    def __repr__(self):
        return "<ProjectDomain: {}>".format(self.name)


class ProjectType(BaseModel, app_resource('project_types')):
    """项目类型"""
    __tablename__ = 'project_type'

    domain_id = db.Column(db.BigInteger, db.ForeignKey('project_domain.id'), index=True, nullable=False)
    domain = db.relationship('ProjectDomain', lazy='joined', backref=db.backref('types', lazy='subquery'))

    # eg: 咨询，专业业务订单，工单
    name = db.Column(db.String(32), nullable=False, index=True)
    desc = db.Column(db.String(64), nullable=False)

    # 每个域下面类型唯一
    __table_args__ = (db.UniqueConstraint('domain_id', 'name', name='uniq_domain_type'),)

    def to_dict(self):
        return dict(name=self.name, desc=self.desc)

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

    @property
    def current_session(self):
        return self.sessions.filter_by(closed=True).one_or_none()

    @property
    def app_biz_id(self):
        return '%s:%s' % (self.type.app_biz_id, self.biz_id)

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


class ProjectXChat(BaseModel, project_resource('xchat')):
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
    parties = db.relationship('Customer', secondary=project_customer_parties, lazy='joined')

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
    leader = db.relationship('Staff', lazy='joined')
    # 协助人
    assistants = db.relationship('Staff', secondary=project_staff_assistants, lazy='joined')
    # 参与人
    participants = db.relationship('Staff', secondary=project_staff_participants, lazy='joined')

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


class Session(BaseModel, project_resource('sessions', uselist=True)):
    """表示一个客服项目的一次会话"""
    __tablename__ = 'session'

    opened_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    closed = db.Column(db.Boolean, default=False)
    closed_time = db.Column(db.DateTime, nullable=True)

    # 接待者
    handler = db.Column(db.String(32), nullable=False)


class Message(BaseModel, project_resource('messages', uselist=True), session_resource('messages', uselist=True)):
    __tablename__ = 'message'

    channel = db.Column(db.Enum(Channel), default=Channel.cs)
    is_staff = db.Column(db.Boolean)
    uid = db.Column(db.String(32))
    ts = db.Column(db.DateTime, default=db.func.current_timestamp())

    # cs域的消息不会发送到外部通道
    domain = db.Column(db.String(32), nullable=True)

    # cs:text, cs:img, cs:file, cs:voice, xx:yy
    type = db.Column(db.String(24))
    content = db.Column(db.Text)

    def __repr__(self):
        return "<Message: {}>".format(self.id)
