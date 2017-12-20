from app import db
from app.service.models import App
from app.utils import dbs
from . import app as app_biz


@dbs.transactional
def create_app(app_data):
    password = ''

    if 'password' in app_data:
        password = app_data['password']
        del app_data['password']

    app = App(**app_data)
    app.update_password(password)
    db.session.add(app)

    project_domain_types_data = [dict(domain=domain_item['name'], type=type_item['name'])
                                 for domain_item in app_data.get('project_domains', [])
                                 for type_item in domain_item.get('types', [])
                                 ]
    app_biz.create_or_update_project_domain_types(app, project_domain_types_data)

    return app
