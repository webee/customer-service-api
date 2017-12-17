from flask_restplus import Resource
from app import jwt
from app.apis.jwt import current_staff, require_staff
from ..api import api
from app.apis.serializers.auth import token_data
from app.apis.serializers.staff import staff


@api.route('/auth')
class Auth(Resource):
    @require_staff
    @api.marshal_with(staff)
    def get(self):
        """得到staff信息"""
        return current_staff


@api.route('/auth/refresh_token')
class RefreshToken(Resource):
    @require_staff
    @api.marshal_with(token_data)
    def post(self):
        """刷新staff token"""
        return jwt.encode_token('staff', current_staff)
