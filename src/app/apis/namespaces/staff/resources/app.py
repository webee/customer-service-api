from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.apis.serializers import app as app_ser
from ..serializers import staff_app_tree


@api.route('/app')
class Application(Resource):
    """当前应用"""
    @require_staff
    @api.marshal_with(app_ser.application)
    def get(self):
        """获取当前应用"""
        staff = current_staff

        return staff.app


@api.route('/staff_app_tree')
class StaffApplicationTree(Resource):
    @require_staff
    @api.marshal_with(staff_app_tree)
    def get(self):
        """获取当前客服应用树"""
        return current_staff
