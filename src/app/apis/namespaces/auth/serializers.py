from flask_restplus import fields
from app.apis import api


app_auth_data = api.model('App auth data', {
    'app_name': fields.String(required=True, min_length=1, example='test', description='app name'),
    'app_password': fields.String(required=True, min_length=1, example='test1234', description='app password')
})

customer_auth_data = api.inherit('Customer auth data', app_auth_data, {
    'uid': fields.String(required=True, min_length=1, example='test', description='customer uid')
})

staff_auth_data = api.inherit('Staff auth data', app_auth_data, {
    'uid': fields.String(required=True, min_length=1, example='test', description='staff uid')
})

app_change_password_data = api.inherit('App change password data', app_auth_data, {
    'new_password': fields.String(required=True, min_length=1, description='new password')
})
