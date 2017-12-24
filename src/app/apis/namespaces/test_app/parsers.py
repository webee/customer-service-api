from flask_restplus import reqparse


auth_args = reqparse.RequestParser()
auth_args.add_argument('appid', type=str, required=True)
auth_args.add_argument('appkey', type=str, required=True)


get_ext_data_args = reqparse.RequestParser()
get_ext_data_args.add_argument('domain', type=str, required=True)
get_ext_data_args.add_argument('type', type=str, required=True)
get_ext_data_args.add_argument('biz_id', type=str, required=True)
get_ext_data_args.add_argument('id', type=int, required=True)


access_function_args = reqparse.RequestParser()
access_function_args.add_argument('domain', type=str, required=True)
access_function_args.add_argument('type', type=str, required=True)
access_function_args.add_argument('biz_id', type=str, required=True)
access_function_args.add_argument('id', type=int, required=True)
access_function_args.add_argument('owner', type=str, required=True)
access_function_args.add_argument('uid', type=str, required=False)
access_function_args.add_argument('function', type=str, required=True)
