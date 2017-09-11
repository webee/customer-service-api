from app import db
from .models import App
from .models import Customer, Staff
from .models import ProjectDomain, ProjectType


def create_app(name, password, desc):
    app = App(name=name, password=password, desc=desc)
    db.session.add(app)
    db.session.commit()

    return app


def create_customer(app_id, uid, name):
    """添加客户"""
    customer = Customer(app_id=app_id, uid=uid, name=name)
    db.session.add(customer)
    db.session.commit()

    return customer


def create_staff(app_id, uid, name):
    """添加客服"""
    staff = Staff(app_id=app_id, uid=uid, name=name)
    db.session.add(staff)
    db.session.commit()

    return staff


def create_project_domain(app_id, name, desc):
    """创建项目域"""
    project_domain = ProjectDomain(app_id=app_id, name=name, desc=desc)
    db.session.add(project_domain)
    db.session.commit()
    return project_domain


def create_project_type(app_id, domain_id, name, desc):
    """创建项目类型"""
    project_type = ProjectType(app_id=app_id, domain_id=domain_id, name=name, desc=desc)
    db.session.add(project_type)
    db.session.commit()

    return project_type
