from app import dbs
from app.service.models import ProjectDomain, ProjectType
from app.service.models import Project
from app.biz import xchat as xchat_biz


@dbs.transactional
def create_project(app, data):
    project_domain = app.project_domains.filter_by(name=data['domain']).one()
    project_type = project_domain.types.filter_by(name=data['type']).one()

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
        chat_id = xchat_biz.create_chat(project)
        assert chat_id == project.xchat.chat_id, 'chat_id should not change'

    dbs.session.add(project)

    return project
