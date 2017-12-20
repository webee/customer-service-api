from flask_restplus import Resource
from ..api import api
from app.apis.jwt import require_staff
from app.apis.utils import xfiles
from app.apis.serializers.auth import token_data


@api.route('/xfiles')
class XFiles(Resource):
    @require_staff
    @api.marshal_with(token_data)
    def get(self):
        """获取xfiles信息"""
        return xfiles.encode_token()
