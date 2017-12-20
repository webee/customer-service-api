import os
from app.biz import app as app_biz, create_app
from . import sample_data


def init_data():
    # project domain/type
    if os.getenv('env') != 'prod':
        init_test_data()

    init_prod_data()


def init_test_data():
    app = create_app(dict(name='test', password='test1234', title='测试应用', desc='测试应用客服', project_domains=[
        dict(name='test', title='测试', desc='测试域', types=[
            dict(name='test', title='测试', desc='测试类型')
        ]),
        dict(name='test2', type='测试', title='测试域', types=[
            dict(name='test', title='测试', desc='测试类型'),
            dict(name='test2', title='测试2', desc='测试类型2'),
        ]),
    ], appid='cs', appkey='cs1234', urls={
        'getToken': 'http://test.com/api/getToken',
        'getExtData': 'http://test.com/api/getExtData',
        'accessFunction': 'http://test.com/api/accessFunction',
        'sendChannelMsg': 'http://test.com/api/sendChannelMsg',
    }, access_functions=['customerDetails'], staff_label_tree=sample_data.test_staff_label_tree))

    # project_domain_type
    # app_biz.create_or_update_project_domain_type(
    #     dict(domain='test', type='test', access_functions=[], class_label_tree={}))

    # customer
    app_biz.batch_create_or_update_customers(app, sample_data.test_customers_data)
    # staff
    app_biz.batch_create_or_update_staffs(app, sample_data.test_staffs_data)

    # projects
    for project_data in sample_data.test_projects_data:
        app_biz.create_project(app, project_data)


def init_prod_data():
    app = create_app(dict(name='qqxb', password='qqxb1234', title='亲亲小保', desc='亲亲小保客服', project_domains=[
        dict(name='personal', title='个人', desc='个人域', types=[
            dict(name='consultation', title='咨询', desc='咨询类型'),
            dict(name='biz_order', title='专项业务订单', desc='专项业务订单类型'),
        ]),
        dict(name='employee', title='员工', desc='员工域', types=[
            dict(name='consultation', title='咨询', desc='咨询类型'),
            dict(name='biz_order', title='专项业务订单', desc='专项业务订单类型'),
        ]),
        dict(name='enterprise', title='企业', desc='企业域', types=[
            dict(name='consultation', title='咨询', desc='咨询类型'),
            dict(name='biz_order', title='专项业务订单', desc='专项业务订单类型'),
            dict(name='work_order', title='工单', desc='工单类型'),
        ]),
    ], appid='cs', appkey='cs1234', urls={
        'getToken': 'http://qqxb.com/api/getToken',
        'getExtData': 'http://qqxb.com/api/getExtData',
        'accessFunction': 'http://qqxb.com/api/accessFunction',
        'sendChannelMsg': 'http://qqxb.com/api/sendChannelMsg',
    }, access_functions=['addRemark', 'addTask', 'customerDetails'], staff_label_tree={}))

    # customer
    app.create_customer('test', '测试客户')
    # staff
    app.create_staff('test', '测试客服', [['self', '']])
