from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.apis.serializers import app as app_ser


@api.route('/app')
class Application(Resource):
    """当前应用"""
    @require_staff
    @api.marshal_with(app_ser.application)
    def get(self):
        """获取当前应用"""
        staff = current_staff

        return staff.app
