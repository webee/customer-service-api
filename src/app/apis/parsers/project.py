from flask_restplus import reqparse, inputs

# fetch msgs 参数
fetch_msgs_arguments = reqparse.RequestParser()
fetch_msgs_arguments.add_argument('lid', type=int, required=False, help='left id')
fetch_msgs_arguments.add_argument('rid', type=int, required=False, help='right id')
fetch_msgs_arguments.add_argument('limit', type=int, required=False, help='count limit count')
fetch_msgs_arguments.add_argument('desc', type=inputs.boolean, required=False, help='order by msg id desc')
fetch_msgs_arguments.add_argument('domain', type=str, required=False, help='message domain')
fetch_msgs_arguments.add_argument('type', type=str, action='append', dest='types', required=False, help='message type')
