from app import jwt
from app.service.models import App, Customer, Staff


def app_token_payload(app):
    return dict(app_name=app.name)


def customer_token_payload(customer):
    return dict(app_name=customer.app.name, uid=customer.uid)


def staff_token_payload(staff):
    return dict(app_name=staff.app.name, uid=staff.uid)


@jwt.as_payload_handler
def payload(role, identity):
    if role == 'app':
        return app_token_payload(identity)
    elif role == 'customer':
        return customer_token_payload(identity)
    elif role == 'staff':
        return staff_token_payload(identity)


@jwt.as_identity_handler
def identity(role, payload):
    if role == 'app':
        return App.query.filter_by(name=payload['app_name']).one_or_none()
    elif role == 'customer':
        return Customer.query.filter(App.name == payload['app_name'], Customer.uid == payload['uid']).one_or_none()
    elif role == 'staff':
        return Staff.query.filter(App.name == payload['app_name'], Staff.uid == payload['uid']).one_or_none()
