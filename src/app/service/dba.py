from app import db
from .models import ProjectDomain, ProjectType
from .models import Customer, Staff


def create_project_domain(name, desc):
    """创建项目域"""
    project_domain = ProjectDomain(name=name, desc=desc)
    db.session.add(project_domain)
    db.session.commit()
    return project_domain


def create_project_type(domain_id, name, desc):
    """创建项目类型"""
    project_type = ProjectType(domain_id=domain_id, name=name, desc=desc)
    db.session.add(project_type)
    db.session.commit()

    return project_type


def create_customer(uid, name):
    """添加客户"""
    customer = Customer(uid=uid, name=name)
    db.session.add(customer)
    db.session.commit()

    return customer


def create_staff(uid, name):
    """添加客服"""
    staff = Staff(uid=uid, name=name)
    db.session.add(staff)
    db.session.commit()

    return staff
