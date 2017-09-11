import os
from app.service.dba import create_app
from app.service.dba import create_project_domain, create_project_type
from app.service.dba import create_customer, create_staff


def init_data():
    # project domain/type
    if os.getenv('env') != 'prod':
        init_test_data()

    init_prod_data()


def init_test_data():
    app = create_app('test', 'test1234', '测试应用')

    # customer
    create_customer(app.id, 'test_001', '测试客户#1')
    create_customer(app.id, 'test_002', '测试客户#2')
    create_customer(app.id, 'test_003', '测试客户#3')

    # staff
    create_staff(app.id, 'test_01', '测试客服#1')
    create_staff(app.id, 'test_02', '测试客服#2')
    create_staff(app.id, 'test_03', '测试客服#3')
    create_staff(app.id, 'test_04', '测试客服#4')
    create_staff(app.id, 'test_05', '测试客服#5')

    # domain/type
    project_domain = create_project_domain(app.id, 'test', '测试')
    create_project_type(app.id, project_domain.id, 'test', '测试')

    # projects
    pass


def init_prod_data():
    app = create_app('qqxb', 'qqxb1234', '亲亲小保')
    project_domain = create_project_domain(app.id, 'personal', '个人')
    create_project_type(app.id, project_domain.id, 'consultation', '咨询')
    create_project_type(app.id, project_domain.id, 'biz_order', '专项业务订单')

    project_domain = create_project_domain(app.id, 'employee', '员工')
    create_project_type(app.id, project_domain.id, 'consultation', '咨询')
    create_project_type(app.id, project_domain.id, 'biz_order', '专项业务订单')

    project_domain = create_project_domain(app.id, 'enterprise', '企业')
    create_project_type(app.id, project_domain.id, 'consultation', '咨询')
    create_project_type(app.id, project_domain.id, 'biz_order', '专项业务订单')
    create_project_type(app.id, project_domain.id, 'work_order', '工单')

