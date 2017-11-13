import json
from app import dbs
from app.service.models import Project, ProjectStaffs, ProjectCustomers
from . import app as app_m


@dbs.transactional
def create_or_update_customers(proj, data):
    parties = app_m.create_or_update_customers(proj.app, data['parties'])

    pc = proj.customers
    if pc is None:
        pc = ProjectCustomers(project=proj, parties=parties)
    else:
        pc.parties = parties
    dbs.session.add(pc)

    return pc


@dbs.transactional
def create_or_update_staffs(proj, data):
    leader = app_m.create_or_update_staff(proj.app, data['leader'])
    assistants = app_m.create_or_update_staffs(proj.app, data['assistants'])
    participants = app_m.create_or_update_staffs(proj.app, data['participants'])

    ps = proj.staffs
    if ps is None:
        ps = ProjectStaffs(project=proj, leader=leader, assistants=assistants, participants=participants)
    else:
        ps.leader = leader
        ps.assistants = assistants
        ps.participants = participants

    dbs.session.add(ps)

    return ps


@dbs.transactional
def create_or_update_meta_data(proj, data):
    proj.meta_data = [proj.create_meta_data_item(item.get('key'),
                                                 json.dumps(item.get('type'), ensure_ascii=False),
                                                 json.dumps(item.get('value'), ensure_ascii=False),
                                                 item.get('label'),
                                                 item.get('index')) for item in data]
    dbs.session.add(proj)
