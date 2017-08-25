from app import dbs
from app.service.models import App
from app.service.models import ProjectDomain, ProjectType
from app.service.models import Project


@dbs.transactional
def create_project(app_id, data):
    app = App.t_query.get(app_id)
    project_type = ProjectType.t_query.filter(ProjectType.name == data['type'],
                                              ProjectDomain.name == data['domain'],
                                              App.id == app.id).one()

    customers = app.create_project_customers(data['customers'])
    staffs = app.create_project_staffs(data['staffs'])
    biz_id = data['biz_id']

    project = Project(type=project_type, biz_id=biz_id, customers=customers, staffs=staffs)
    dbs.session.add(project)

    # create xchat chat

    return project

