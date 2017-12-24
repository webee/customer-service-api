from flask_restplus import reqparse

# fetch msgs 参数
fetch_msgs_arguments = reqparse.RequestParser()
fetch_msgs_arguments.add_argument('lid', type=int, required=False, help='left id')
fetch_msgs_arguments.add_argument('rid', type=int, required=False, help='right id')
fetch_msgs_arguments.add_argument('limit', type=int, required=False, help='count limit count')
fetch_msgs_arguments.add_argument('desc', type=bool, required=False, help='order by msg id desc')

access_function_args = reqparse.RequestParser()
access_function_args.add_argument('uid', type=str, required=False)
