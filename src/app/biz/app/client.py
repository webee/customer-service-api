from app.service.models import App
from app import app_clients


def send_channel_msg(app_name, channel, uid, staff, type, content, project_info):
    app = App.query.filter_by(name=app_name).one_or_none()
    if app is None:
        return

    app_client = app_clients.get_client(app.appid, app.appkey, app.urls)

    app_client.send_channel_msg(channel, uid, staff, type, content, project_info)


def fetch_ext_data(app_name, domain, type, biz_id, id=None):
    from . import get_project

    app = App.query.filter_by(name=app_name).one_or_none()
    if app is None:
        return

    app_client = app_clients.get_client(app.appid, app.appkey, app.urls)

    data = app_client.get_ext_data(domain, type, biz_id, id=id)
    proj = get_project(app, id, domain, type, biz_id)
    proj.update_ext_data(data)

    # TODO: notify staff
