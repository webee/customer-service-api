from app import dbs
from .utils import normalize_labels, normalize_data


def create_or_update_project_domain_type(app, data):
    domain = data['domain']
    type = data['type']
    access_functions = data.get('access_functions')
    class_label_tree = data.get('class_label_tree')
    return app.create_project_domain_type(domain, type, access_functions, class_label_tree)


@dbs.transactional
def create_or_update_project_domain_types(app, project_domain_types_data):
    return [create_or_update_project_domain_type(app, project_domain_type) for project_domain_type in
            project_domain_types_data]


def create_or_update_customer(app, data):
    uid = data.get('uid')
    name = data.get('name')
    mobile = data.get('mobile')
    ext_data = normalize_data(data.get('ext_data'))
    return app.create_customer(uid, name, mobile, ext_data)


@dbs.transactional
def create_or_update_customers(app, customers_data):
    return [create_or_update_customer(app, customer) for customer in customers_data]


def create_or_update_staff(app, data):
    uid = data.get('uid')
    name = data.get('name')
    context_labels = normalize_labels(data.get('context_labels'))
    staff = app.create_staff(uid, name, context_labels)
    return staff


@dbs.transactional
def create_or_update_staffs(app, staffs_data):
    return [create_or_update_staff(app, staff) for staff in staffs_data]
