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
    app = create_app('test', 'test1234', '测试应用')

    # customer
    app.create_customer('test_001', '测试客户#1')
    app.create_customer('test_002', '测试客户#2')
    app.create_customer('test_003', '测试客户#3')

    # staff
    app.create_staff('test_01', '测试客服#1')
    app.create_staff('test_02', '测试客服#2')
    app.create_staff('test_03', '测试客服#3')
    app.create_staff('test_04', '测试客服#4')
    app.create_staff('test_05', '测试客服#5')

    # domain/type
    project_domain = app.create_project_domain('test', '测试')
    project_domain.create_project_type('test', '测试')

    # projects
    app_biz.create_project(app, sample_data.test_project_data)


def init_prod_data():
    app = create_app('qqxb', 'qqxb1234', '亲亲小保')
    project_domain = app.create_project_domain('personal', '个人')
    project_domain.create_project_type('consultation', '咨询')
    project_domain.create_project_type('biz_order', '专项业务订单')

    project_domain = app.create_project_domain('employee', '员工')
    project_domain.create_project_type('consultation', '咨询')
    project_domain.create_project_type('biz_order', '专项业务订单')

    project_domain = app.create_project_domain('enterprise', '企业')
    project_domain.create_project_type('consultation', '咨询')
    project_domain.create_project_type('biz_order', '专项业务订单')
    project_domain.create_project_type('work_order', '工单')

