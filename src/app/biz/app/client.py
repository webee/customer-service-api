from app.service.models import App
from app import app_clients
from app.biz.constants import NotifyTypes
from app.biz.notifies import task_project_notify


def send_channel_msg(app_name, channel, uid, staff, type, content, project_info):
    app = App.query.filter_by(name=app_name).one_or_none()
    if app is None:
        return

    app_client = app_clients.get_client(app.appid, app.appkey, app.urls)

    app_client.send_channel_msg(channel, uid, staff, type, content, project_info)


def fetch_ext_data(app_name, domain, type, biz_id, id=None, staff_uid=None):
    from . import get_project

    app = App.query.filter_by(name=app_name).one_or_none()
    if app is None:
        return

    app_client = app_clients.get_client(app.appid, app.appkey, app.urls)

    data = app_client.get_ext_data(domain, type, biz_id, id=id)
    proj = get_project(app, id, domain, type, biz_id)
    proj.update_ext_data(data)

    handler = None
    if staff_uid is not None:
        handler = app.staffs.filter_by(uid=staff_uid).one_or_none()
    # # notify client
    task_project_notify(proj, NotifyTypes.MY_HANDLING_PROJECT, dict(projectID=proj.id), handler=handler)
