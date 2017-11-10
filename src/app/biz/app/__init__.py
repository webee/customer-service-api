import re
from sqlalchemy.orm.exc import NoResultFound
from app import dbs
from app.errors import BizError
from app.service.models import Project
from app.biz import xchat as xchat_biz

NS_PT = re.compile(r':')


@dbs.transactional
def create_project(app, data):
    try:
        project_domain = app.project_domains.filter_by(name=data['domain']).one()
        project_type = project_domain.types.filter_by(name=data['type']).one()
    except NoResultFound:
        raise BizError('project domain/type not exists', dict(domain=data['domain'], type=data['type']), 400)

    biz_id = data['biz_id']
    start_msg_id = data.get('start_msg_id', 0)
    project = project_type.projects.filter_by(biz_id=biz_id).one_or_none()
    if project is None:
        owner = app.create_or_update_customer(data['owner'])
        project = Project(app=app, domain=project_type.domain, type=project_type, biz_id=biz_id, owner=owner,
                          start_msg_id=start_msg_id, msg_id=start_msg_id)
        project.create_customers(data['customers'])
        project.create_staffs(data['staffs'])
        chat_id = xchat_biz.create_chat(project)
        project.create_xchat(chat_id)
    else:
        project.owner = app.create_or_update_customer(data['owner'])
        project.customers.update(data['customers'])
        project.staffs.update(data['staffs'])
        # update xchat chat
        chat_id = xchat_biz.create_chat(project)
        assert chat_id == project.xchat.chat_id, 'chat_id should not change'

    dbs.session.add(project)

    return project


def parse_app_uid(app_uid):
    parts = app_uid.split(':', 2)
    if len(parts) == 3:
        return True, parts
    return False, parts
