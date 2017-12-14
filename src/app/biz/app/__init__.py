import re
from sqlalchemy.orm.exc import NoResultFound
from app import dbs
from app import errors
from app.errors import BizError
from app.service.models import App, UserType, Project
from app.biz import xchat as xchat_biz
from app.biz.ds import parse_app_user_id_from_xchat_uid
from app.utils.commons import batch_split
from app.biz.notifies import task_project_notify, task_app_notify
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
        leader = app_m.create_or_update_staff(app, data['leader'])
        customers = app_m.create_or_update_customers(app, data['customers'])
        project = Project(app=app, domain=project_domain, type=project_type, biz_id=biz_id, owner=owner, leader=leader,
                          customers=customers, start_msg_id=start_msg_id, msg_id=start_msg_id)

        # xchat
        chat_id = xchat_biz.create_chat(project)
        project.create_xchat(chat_id)

        # meta data
        proj_m.create_or_update_meta_data(project, data['meta_data'])
    else:
        project.owner = app_m.create_or_update_customer(app, data['owner'])
        project.leader = app_m.create_or_update_staff(app, data['leader'])
        project.customers = app_m.create_or_update_customers(app, data['customers'])

        # update xchat chat
        chat_id = xchat_biz.create_chat(project)
        assert chat_id == project.xchat.chat_id, 'chat_id should not change'

        # meta data
        proj_m.create_or_update_meta_data(project, data['meta_data'])

    dbs.session.add(project)

    return project


def create_or_update_project_meta_data(proj, data):
    proj_m.create_or_update_meta_data(proj, data)


def batch_create_or_update_customers(app, data):
    for split_data in batch_split(data, 100):
        app_m.create_or_update_customers(app, split_data)


def batch_create_or_update_staffs(app, data):
    for split_data in batch_split(data, 100):
        app_m.create_or_update_staffs(app, split_data)


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
        # TODO: 通知所有在线的staffs该staff的状态改变
        # task_app_notify(app_uid, 'user', dict(user_type='staff', uid=customer.uid))
    elif user_type == UserType.customer:
        customer = app.customers.filter_by(uid=uid).one_or_none()
        if customer is None:
            return
        customer.update_online(online)

        # update as customer projects' online status
        projs = customer.as_customer_projects.all()
        _update_project_statuses(customer, projs, online)


def _update_project_statuses(customer, projects, online):
    for project in projects:
        prev_is_online = project.is_online
        if online:
            project.update_online(online)
        else:
            # 离线
            # any of project's customer are online
            proj_online = any([c.is_online for c in project.customers])
            project.update_online(proj_online, offline_check=False)

        current_session = project.current_session
        if current_session is not None and prev_is_online != project.is_online:
            # # notify client
            task_project_notify(project, 'my_handling.sessions', dict(sessionID=project.current_session_id))
            task_app_notify(current_session.handler, 'user', dict(user_type='customer', uid=customer.uid))
