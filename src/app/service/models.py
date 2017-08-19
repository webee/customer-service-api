import enum
from app import db


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


class BaseModel(db.Model):
    """基本模型"""
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class ProjectDomain(BaseModel):
    """项目域"""
    __tablename__ = 'project_domain'

    # 个人，员工，企业
    name = db.Column(db.String(32), nullable=False, unique=True, index=True)
    desc = db.Column(db.String(64), nullable=False)

    types = db.relationship('ProjectType', lazy='subquery')

    def to_dict(self):
        return dict(name=self.name, desc=self.desc, types=[t.to_dict() for t in self.types])

    def __repr__(self):
        return "<ProjectDomain: {}>".format(self.name)


class ProjectType(BaseModel):
    """项目类型"""
    __tablename__ = 'project_type'

    domain_id = db.Column(db.BigInteger, db.ForeignKey('project_domain.id'), index=True, nullable=False)
    domain = db.relationship('ProjectDomain', lazy='joined')

    # 咨询，专业业务订单，工单
    name = db.Column(db.String(32), nullable=False)
    desc = db.Column(db.String(64), nullable=False)

    projects = db.relationship('Project', lazy='dynamic')

    __table_args__ = (db.UniqueConstraint('domain_id', 'name', name='uniq_domain_type'),)

    def to_dict(self):
        return dict(name=self.name, desc=self.desc)

    def __repr__(self):
        return "<ProjectType: {}:{}>".format(self.domain.name, self.name)


class Project(BaseModel):
    """表示一个客服项目"""
    __tablename__ = 'project'

    # 类型
    type_id = db.Column(db.BigInteger, db.ForeignKey('project_type.id'), index=True, nullable=False)
    type = db.relationship('ProjectType', lazy='joined')

    # 相关客户
    customers_id = db.Column(db.BigInteger, db.ForeignKey('project_customers.id'), nullable=False)
    customers = db.relationship('ProjectCustomers')

    # 相关客服
    staffs_id = db.Column(db.BigInteger, db.ForeignKey('project_staffs.id'), nullable=False)
    staffs = db.relationship('ProjectStaffs')

    # 项目信息
    # # 元数据
    meta_data_id = db.Column(db.BigInteger, db.ForeignKey('project_meta_data.id'), nullable=False)
    meta_data = db.relationship('ProjectMetaData')

    # # 扩展数据
    ext_data_id = db.Column(db.BigInteger, db.ForeignKey('project_ext_data.id'), nullable=False)
    ext_data = db.relationship('ProjectExtData')

    # xchat

    # 项目会话
    sessions = db.relationship('Session', lazy='dynamic')
    messages = db.relationship('Message', lazy='dynamic')

    @property
    def current_session(self):
        return self.sessions.filter_by(closed=True).one_or_none()

    def __repr__(self):
        return "<Project: {}:{}.{}>".format(self.type.domain.name, self.type.name, self.id)


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


class ProjectCustomers(BaseModel):
    """项目相关客户"""
    __tablename__ = 'project_customers'

    project = db.relationship('Project', uselist=False)
    # 当事人
    parties = db.relationship('Customer', secondary=project_customer_parties)


class ProjectStaffs(BaseModel):
    """项目相关客服"""
    __tablename__ = 'project_staffs'

    project = db.relationship('Project', uselist=False)
    # 负责人
    leader_id = db.Column(db.BigInteger, db.ForeignKey('staff.id'), nullable=False)
    leader = db.relationship('Staff')
    # 协助人
    assistants = db.relationship('Staff', secondary=project_staff_assistants)
    # 参与人
    participants = db.relationship('Staff', secondary=project_staff_participants)


class Customer(BaseModel):
    """客户"""
    __tablename__ = 'customer'

    uid = db.Column(db.String(32), nullable=False, unique=True)
    name = db.Column(db.String(16), nullable=False)


class Staff(BaseModel):
    """客服"""
    __tablename__ = 'staff'

    uid = db.Column(db.String(32), nullable=False, unique=True)
    name = db.Column(db.String(16), nullable=False)


class ProjectMetaData(BaseModel):
    """项目元数据"""
    __tablename__ = 'project_meta_data'

    project = db.relationship('Project', uselist=False)
    pass


class ProjectExtData(BaseModel):
    """项目扩展数据"""
    __tablename__ = 'project_ext_data'

    project = db.relationship('Project', uselist=False)
    pass


class Session(BaseModel):
    """表示一个客服项目的一次会话"""
    __tablename__ = 'session'

    project_id = db.Column(db.BigInteger, db.ForeignKey('project.id'), index=True, nullable=False)
    project = db.relationship('Project', lazy='joined')

    opened_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    closed = db.Column(db.Boolean, default=False)
    closed_time = db.Column(db.DateTime, nullable=True)

    # 接待者
    handler = db.Column(db.String(32), nullable=False)

    messages = db.relationship('Message', lazy='dynamic')


class Message(BaseModel):
    __tablename__ = 'message'

    project_id = db.Column(db.BigInteger, db.ForeignKey('project.id'), index=True, nullable=False)
    project = db.relationship('Project')

    session_id = db.Column(db.BigInteger, db.ForeignKey('session.id'), index=True, nullable=False)
    session = db.relationship('Session')

    channel = db.Column(db.Enum(Channel), default=Channel.cs)
    uid = db.Column(db.String(32))
    ts = db.Column(db.DateTime, default=db.func.current_timestamp())

    # cs域的消息不会发送到外部通道
    domain = db.Column(db.String(32), nullable=True)

    # cs:text, cs:img, cs:file, cs:voice, xx:yy
    type = db.Column(db.String(24))
    content = db.Column(db.Text)

    def __repr__(self):
        return "<Message: {}>".format(self.id)
