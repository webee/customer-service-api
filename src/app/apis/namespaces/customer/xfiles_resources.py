from flask_restplus import Resource
from .api import api
from app.apis.jwt import require_customer
from app.apis.utils import xfiles


@api.route('/xfiles')
class XFiles(Resource):
    @require_customer
    def get(self):
        """获取xfiles信息"""
        return dict(token=xfiles.encode_token())