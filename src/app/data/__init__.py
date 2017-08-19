import app
from app.service.dba import create_project_domain, create_project_type
from app.service.dba import create_customer, create_staff


def init_data():
    # project domain/type
    if app.config.__env_name__ != 'prod':
        project_domain = create_project_domain('test', '测试')
        create_project_type(project_domain.id, 'test', '测试')

    project_domain = create_project_domain('personal', '个人')
    create_project_type(project_domain.id, 'consultation', '咨询')
    create_project_type(project_domain.id, 'special_biz_order', '专项业务订单')

    project_domain = create_project_domain('employee', '员工')
    create_project_type(project_domain.id, 'consultation', '咨询')
    create_project_type(project_domain.id, 'special_biz_order', '专项业务订单')

    project_domain = create_project_domain('enterprise', '企业')
    create_project_type(project_domain.id, 'consultation', '咨询')
    create_project_type(project_domain.id, 'special_biz_order', '专项业务订单')
    create_project_type(project_domain.id, 'work_order', '工单')

    # customer
    create_customer('test_001', '测试客户#1')
    create_customer('test_002', '测试客户#2')
    create_customer('test_003', '测试客户#3')

    # staff
    create_staff('test_01', '测试客服#1')
    create_staff('test_02', '测试客服#2')
    create_staff('test_03', '测试客服#3')
