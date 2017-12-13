from flask_restplus import Resource
from ..api import api
from app.apis.jwt import require_staff
from app.apis.utils import xfiles


@api.route('/xfiles')
class XFiles(Resource):
    @require_staff
    def get(self):
        """获取xfiles信息"""
        return dict(token=xfiles.encode_token())
