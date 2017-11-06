
from flask_restplus import reqparse

# 分页参数
uid_args = reqparse.RequestParser()
uid_args.add_argument('uid', type=str, required=True, help="uid")
