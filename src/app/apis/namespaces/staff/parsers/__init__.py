from flask_restplus import reqparse

access_function_args = reqparse.RequestParser()
access_function_args.add_argument('uid', type=str, required=False)
