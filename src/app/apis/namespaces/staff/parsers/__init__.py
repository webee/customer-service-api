from flask_restplus import reqparse, inputs
from app.apis.parsers import pagination_arguments
from app.apis.parsers.types import ContextLabel, DateTimeRange, NumberRange

access_function_args = reqparse.RequestParser()
access_function_args.add_argument('uid', type=str, required=False)

fetch_staffs_args = pagination_arguments.copy()
fetch_staffs_args.add_argument('uid', type=str, required=False)
fetch_staffs_args.add_argument('context_label', type=ContextLabel(), required=False)
fetch_staffs_args.add_argument('is_online', type=inputs.boolean, required=False)
fetch_staffs_args.add_argument('is_deleted', type=inputs.boolean, required=False)
fetch_staffs_args.add_argument('sorter', type=str, required=False)
fetch_staffs_args.add_argument('order', type=str, required=False)

fetch_handling_sessions_args = pagination_arguments.copy()
fetch_handling_sessions_args.add_argument('handler', type=str, required=False)
fetch_handling_sessions_args.add_argument('owner', type=str, required=False)
fetch_handling_sessions_args.add_argument('customer', type=str, required=False)
fetch_handling_sessions_args.add_argument('filter_self', type=str, required=False)
fetch_handling_sessions_args.add_argument('context_label', type=ContextLabel(), required=False)
fetch_handling_sessions_args.add_argument('is_online', type=inputs.boolean, required=False)
fetch_handling_sessions_args.add_argument('unhandled_msg_count_range', type=NumberRange(int), required=False)
fetch_handling_sessions_args.add_argument('msg_ts_range', type=DateTimeRange(), required=False)
fetch_handling_sessions_args.add_argument('tag', type=str, required=False)
fetch_handling_sessions_args.add_argument('sorter', type=str, required=False)
fetch_handling_sessions_args.add_argument('order', type=str, required=False)

fetch_handled_sessions_args = pagination_arguments.copy()
fetch_handled_sessions_args.add_argument('handler', type=str, required=False)
fetch_handled_sessions_args.add_argument('filter_self', type=str, required=False)
fetch_handled_sessions_args.add_argument('owner', type=str, required=False)
fetch_handling_sessions_args.add_argument('customer', type=str, required=False)
fetch_handled_sessions_args.add_argument('context_label', type=ContextLabel(), required=False)
fetch_handled_sessions_args.add_argument('is_online', type=inputs.boolean, required=False)
fetch_handled_sessions_args.add_argument('closed_ts_range', type=DateTimeRange(), required=False)
fetch_handled_sessions_args.add_argument('tag', type=str, required=False)
fetch_handled_sessions_args.add_argument('sorter', type=str, required=False)
fetch_handled_sessions_args.add_argument('order', type=str, required=False)
