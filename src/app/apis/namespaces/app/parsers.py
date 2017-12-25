from flask_restplus import reqparse

try_handle_project_arguments = reqparse.RequestParser()
try_handle_project_arguments.add_argument('uid', type=str, required=True, help='staff uid')
