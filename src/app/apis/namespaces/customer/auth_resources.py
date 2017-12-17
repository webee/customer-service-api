from flask_restplus import Resource
from app import jwt
from app.apis.jwt import current_customer, require_customer
from .api import api
from app.apis.serializers.auth import token_data
from app.apis.serializers.customer import customer


@api.route('/auth')
class Auth(Resource):
    @require_customer
    @api.marshal_with(customer)
    def get(self):
        """得到customer信息"""
        return current_customer


@api.route('/auth/refresh_token')
class RefreshToken(Resource):
    @require_customer
    @api.marshal_with(token_data)
    def post(self):
        """刷新customer token"""
        return jwt.encode_token('customer', current_customer)
