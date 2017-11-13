from app import dbs


def create_or_update_customer(app, data):
    uid = data.get('uid')
    name = data.get('name')
    return app.create_customer(uid, name)


@dbs.transactional
def create_or_update_customers(app, customers_data):
    return [create_or_update_customer(app, customer) for customer in customers_data]


def create_or_update_staff(app, data):
    uid = data.get('uid')
    name = data.get('name')
    staff = app.create_staff(uid, name)
    return staff


@dbs.transactional
def create_or_update_staffs(app, staffs_data):
    return [create_or_update_staff(app, staff) for staff in staffs_data]

