from flask import request
from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff


@api.route('/projects')
class ProjectCollection(Resource):
    """项目集合"""
    @require_staff
    def get(self):
        """获取所有项目类型"""
        staff = current_staff
        return None


@api.route('/project_types')
class ProjectTypeItem(Resource):
    """项目类型集合"""
    @require_staff
    def get(self):
        """获取所有项目类型"""
        staff = current_staff

        return None
