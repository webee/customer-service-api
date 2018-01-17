from app import db
from app.service.models import App
from app.utils import dbs
from . import app as app_biz


@dbs.transactional
def create_app(data):
    name = data['name']
    password = data['password']
    title = data['title']
    desc = data['desc']
    project_domains = data.get('project_domains', [])
    appid = data['appid']
    appkey = data['appkey']

    app = App(name=name, title=title, desc=desc, project_domains=project_domains, appid=appid, appkey=appkey)
    app.update_password(password)
    app.update_urls(data.get('urls'))
    app.update_access_functions(data.get('access_functions'))
    app.update_staff_label_tree(data.get('staff_label_tree'))
    app.update_configs(data.get('configs'))

    db.session.add(app)

    project_domain_types_data = [dict(domain=domain_item['name'], type=type_item['name'])
                                 for domain_item in project_domains
                                 for type_item in domain_item.get('types', [])
                                 ]
    app_biz.create_or_update_project_domain_types(app, project_domain_types_data)

    return app


@dbs.transactional
def update_app(app, data):
    if 'appid' in data:
        app.appid = data['appid']
    if 'appkey' in data:
        app.appkey = data['appkey']
    app.update_urls(data.get('urls'))
    app.update_access_functions(data.get('access_functions'))
    app.update_staff_label_tree(data.get('staff_label_tree'))
    app.update_configs(data.get('configs'))

    dbs.session.add(app)

    return app
