import os
from app.service.dba import create_app
from app.biz import app as app_biz
from . import sample_data


def init_data():
    # project domain/type
    if os.getenv('env') != 'prod':
        init_test_data()

    init_prod_data()


def init_test_data():
    app = create_app('test', 'test1234', '测试应用', '测试应用客服')

    # customer
    app.create_customer('test', '测试客户')
    app.create_customer('test_001', '测试客户#1')
    app.create_customer('test_002', '测试客户#2')
    app.create_customer('test_003', '测试客户#3')

    # staff
    app.create_staff('test', '测试客服')
    app.create_staff('test_01', '测试客服#1')
    app.create_staff('test_02', '测试客服#2')
    app.create_staff('test_03', '测试客服#3')
    app.create_staff('test_04', '测试客服#4')
    app.create_staff('test_05', '测试客服#5')

    # domain/type
    project_domain = app.create_project_domain('test', '测试', '测试域')
    project_domain.create_project_type('test', '测试', '测试类型')

    project_domain = app.create_project_domain('test2', '测试2', '测试域2')
    project_domain.create_project_type('test', '测试', '测试类型')
    project_domain.create_project_type('test2', '测试2', '测试类型2')

    # projects
    for project_data in sample_data.test_projects_data:
        app_biz.create_project(app, project_data)


def init_prod_data():
    app = create_app('qqxb', 'qqxb1234', '亲亲小保', '亲亲小保客服')
    # customer
    app.create_customer('test', '测试客户')

    # staff
    app.create_staff('test', '测试客服')

    project_domain = app.create_project_domain('personal', '个人', '个人域')
    project_domain.create_project_type('consultation', '咨询', '咨询类型')
    project_domain.create_project_type('biz_order', '专项业务订单', '专项业务订单类型')

    project_domain = app.create_project_domain('employee', '员工', '员工域')
    project_domain.create_project_type('consultation', '咨询', '咨询类型')
    project_domain.create_project_type('biz_order', '专项业务订单', '专项业务订单类型')

    project_domain = app.create_project_domain('enterprise', '企业', '企业域')
    project_domain.create_project_type('consultation', '咨询', '咨询类型')
    project_domain.create_project_type('biz_order', '专项业务订单', '专项业务订单类型')
    project_domain.create_project_type('work_order', '工单', '工单类型')

