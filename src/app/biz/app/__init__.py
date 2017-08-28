from app import dbs
from app.service.models import App
from app.service.models import ProjectDomain, ProjectType
from app.service.models import Project
from app.biz import xchat as xchat_biz


@dbs.transactional
def create_project(app_id, data):
    app = App.t_query.get(app_id)
    project_type = ProjectType.t_query.filter(ProjectType.name == data['type'],
                                              ProjectDomain.name == data['domain'],
                                              App.id == app.id).one()

    biz_id = data['biz_id']
    project = Project.t_query.filter_by(type_id=project_type.id, biz_id=biz_id).one_or_none()
    if project is None:
        project = Project(type=project_type, biz_id=biz_id)

        project.customers = app.create_project_customers(data['customers'])
        project.staffs = app.create_project_staffs(data['staffs'])
    else:
        project.customers.update_members(app, data['customers'])
        project.staffs.update_members(app, data['staffs'])

    dbs.session.add(project)
    if project.id is None:
        dbs.session.flush()

    # create xchat chat
    xchat_biz.create_project_chat(project)

    return project
