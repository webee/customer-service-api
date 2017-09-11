from flask_restplus import reqparse

# 分页参数
pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('page', type=int, required=False, default=1, help='Page number')
pagination_arguments.add_argument('per_page', type=int, required=False, default=10, help='Results per page {error_msg}')
