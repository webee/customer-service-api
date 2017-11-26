import re
from sqlalchemy.orm.exc import NoResultFound
from app import dbs
from app import errors
from app.errors import BizError
from app.service.models import App, UserType, Project
from app.biz import xchat as xchat_biz
from app.biz.ds import parse_app_user_id_from_xchat_uid
from app.utils.commons import batch_split
from . import app as app_m
from . import proj as proj_m


NS_PT = re.compile(r':')


@dbs.transactional
def create_project(app, data):
    try:
        project_domain = app.project_domains.filter_by(name=data['domain']).one()
        project_type = project_domain.types.filter_by(name=data['type']).one()
    except NoResultFound:
        raise BizError(errors.ERR_ITEM_NOT_FOUND, 'project domain/type not exists',
                       dict(domain=data['domain'], type=data['type']))

    biz_id = data['biz_id']
    start_msg_id = data.get('start_msg_id', 0)
    project = project_type.projects.filter_by(biz_id=biz_id).one_or_none()
    if project is None:
        owner = app_m.create_or_update_customer(app, data['owner'])
        project = Project(app=app, domain=project_type.domain, type=project_type, biz_id=biz_id, owner=owner,
                          start_msg_id=start_msg_id, msg_id=start_msg_id)
        proj_m.create_or_update_customers(project, data['customers'])
        proj_m.create_or_update_staffs(project, data['staffs'])

        # xchat
        chat_id = xchat_biz.create_chat(project)
        project.create_xchat(chat_id)

        # meta data
        proj_m.create_or_update_meta_data(project, data['meta_data'])
    else:
        project.owner = app_m.create_or_update_customer(app, data['owner'])
        proj_m.create_or_update_customers(project, data['customers'])
        proj_m.create_or_update_staffs(project, data['staffs'])

        # update xchat chat
        chat_id = xchat_biz.create_chat(project)
        assert chat_id == project.xchat.chat_id, 'chat_id should not change'

        # meta data
        proj_m.create_or_update_meta_data(project, data['meta_data'])

    dbs.session.add(project)

    return project


def create_or_update_project_meta_data(proj, data):
    proj_m.create_or_update_meta_data(proj, data)


def parse_app_uid(app_uid):
    parts = app_uid.split(':', 2)
    if len(parts) == 3:
        return True, parts
    return False, parts


def sync_user_statuses(user_statuses):
    app_user_statuses = {}
    for user_status in user_statuses:
        app_name, user_type, uid = parse_app_user_id_from_xchat_uid(user_status['user'])
        online = user_status['status'] == 'online'
        app_user_statuses.setdefault(app_name, []).append((user_type, uid, online))
    for app_name, statuses in app_user_statuses.items():
        app = App.query.filter_by(name=app_name).one_or_none()
        if app is None:
            continue
        for split_statuses in batch_split(statuses, 100):
            update_user_statuses(app, split_statuses)


@dbs.transactional
def update_user_statuses(app, user_statuses):
    for user_status in user_statuses:
        _update_user_status(app, user_status)


def _update_user_status(app, status):
    user_type, uid, online = status
    if user_type == UserType.staff:
        staff = app.staffs.filter_by(uid=uid).one_or_none()
        if staff is None:
            return
        staff.update_online(online)
    elif user_type == UserType.customer:
        customer = app.customers.filter_by(uid=uid).one_or_none()
        if customer is None:
            return
        customer.update_online(online)

        # update as party projects' online status
        pcs = customer.as_party_projects.all()
        _update_project_statuses([pc.project for pc in pcs], online)


def _update_project_statuses(projects, online):
    for project in projects:
        if online:
            project.update_online(online)
        else:
            # 离线
            # any of project's customer parties are online
            proj_online = any([c.is_online for c in project.customers.parties])
            project.update_online(proj_online, offline_check=False)
