from flask_restplus import fields
from .api import api


app_auth_data = api.model('App auth data', {
    'app_name': fields.String(required=True, min_length=1, description='app name'),
    'app_password': fields.String(required=True, min_length=1, description='app password')
})

customer_auth_data = api.inherit('Customer auth data', app_auth_data, {
    'uid': fields.String(required=True, min_length=1, description='customer uid')
})

staff_auth_data = api.inherit('Staff auth data', app_auth_data, {
    'uid': fields.String(required=True, min_length=1, description='staff uid')
})

app_change_password_data = api.model('App change password data', {
    'name': fields.String(required=True, min_length=1, description='app name'),
    'password': fields.String(required=True, min_length=1, description='current password'),
    'new_password': fields.String(required=True, min_length=1, description='new password')
})
