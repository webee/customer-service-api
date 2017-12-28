from flask_restplus import reqparse, inputs
from app.apis.parsers import pagination_arguments
from app.apis.parsers.types import ContextLabel

access_function_args = reqparse.RequestParser()
access_function_args.add_argument('uid', type=str, required=False)

fetch_staffs_args = pagination_arguments.copy()
fetch_staffs_args.add_argument('uid', type=str, required=False)
fetch_staffs_args.add_argument('context_label', type=ContextLabel(), required=False)
fetch_staffs_args.add_argument('is_online', type=inputs.boolean, required=False)
fetch_staffs_args.add_argument('is_deleted', type=inputs.boolean, required=False)
fetch_staffs_args.add_argument('sorter', type=str, required=False)
fetch_staffs_args.add_argument('order', type=str, required=False)
