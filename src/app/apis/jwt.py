from app import jwt
from app.service.models import App, Customer, Staff
from . import api


@jwt.as_auth_required_hook
def auth_required_hook(role, func):
    return api.doc(security=role + '-jwt')(func)


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
        return Customer.query.filter(Customer.app.has(name=payload['app_name']), Customer.uid == payload['uid'],
                                     Staff.is_deleted == False).one_or_none()
    elif role == 'staff':
        return Staff.query.filter(Staff.app.has(name=payload['app_name']), Staff.uid == payload['uid'],
                                  Staff.is_deleted == False).one_or_none()


@jwt.as_identity_secret_handler
def identity_secret(role, identity):
    if role == 'app':
        return identity.password
    elif role == 'customer':
        return identity.app.password
    elif role == 'staff':
        return identity.app.password


require_app = jwt.auth_required('app')
require_customer = jwt.auth_required('customer')
require_staff = jwt.auth_required('staff')

current_application: App = jwt.current_identity
current_customer: Customer = jwt.current_identity
current_staff: Staff = jwt.current_identity
