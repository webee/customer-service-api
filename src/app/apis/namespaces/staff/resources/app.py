from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from ..serializers import staff_app_info


@api.route('/staff_app_info')
class StaffApplicationInfo(Resource):
    @require_staff
    @api.marshal_with(staff_app_info)
    def get(self):
        """获取当前客服应用信息"""
        app = current_staff.app
        project_domains = app.project_domains
        access_functions = app.access_functions

        return dict(app=app, staff=current_staff, project_domains=project_domains, access_functions=access_functions)
