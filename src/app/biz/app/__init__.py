from app import dbs
from app.service.models import App
from app.service.models import ProjectDomain, ProjectType
from app.service.models import Project
from app.biz import xchat as xchat_biz


@dbs.transactional
def create_project(app_id, data):
    app = App.t_query.get(app_id)
    project_type = app.project_types.filter(ProjectType.name == data['type'],
                                            ProjectDomain.name == data['domain']).one()

    biz_id = data['biz_id']
    project = project_type.projects.filter_by(biz_id=biz_id).one_or_none()
    if project is None:
        project = Project(app=app, domain=project_type.domain, type=project_type, biz_id=biz_id)
        project.create_customers(data['customers'])
        project.create_staffs(data['staffs'])
        chat_id = xchat_biz.create_chat(project)
        project.create_xchat(chat_id)
    else:
        project.customers.update(data['customers'])
        project.staffs.update(data['staffs'])
        chat_id = xchat_biz.create_chat(project)
        project.xchat.update(chat_id)

    dbs.session.add(project)

    return project
