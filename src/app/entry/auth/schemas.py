from schema import Schema, And, Optional


new_app_token_schema = Schema({
    'app_name': And(str, len, error='app name is invalid'),
    'app_password': And(str, len, error='app password is invalid')
})


new_customer_token_schema = Schema({
    'app_name': And(str, len, error='app name is invalid'),
    'app_password': And(str, len, error='app password is invalid'),
    'uid': And(str, len, error='customer uid is invalid')
})


new_staff_token_schema = Schema({
    'app_name': And(str, len, error='app name is invalid'),
    'app_password': And(str, len, error='app password is invalid'),
    'uid': And(str, len, error='staff uid is invalid')
})


change_app_password_schema = Schema({
    'password': And(str, len, error='password is invalid'),
    'new_password': And(str, len, error='new password is invalid')
})
