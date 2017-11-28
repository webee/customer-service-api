from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from ..serializers import staff_app_info


@api.route('/staff_app_info')
class StaffApplicationTree(Resource):
    @require_staff
    @api.marshal_with(staff_app_info)
    def get(self):
        """获取当前客服应用信息"""
        return current_staff
