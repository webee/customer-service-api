from flask import request
from flask_restplus import Resource
from .api import api
from . import serializers as ser
from app.apis.serializers import resource_id
from app.biz import app as biz
from app.apis.jwt import current_staff, require_staff


@api.route('/project_types')
class ProjectDomainCollection(Resource):
    """项目域集合"""
    @require_staff
    @api.marshal_with(resource_id)
    def get(self):
        """获取所有项目域"""
        staff = current_staff
        app = staff.app

        data = request.get_json()
        project = biz.create_project(app.id, data)
        return project, 201


@api.route('/project_types')
class ProjectDomainItem(Resource):
    """项目类型集合"""
    @require_staff
    @api.marshal_with(resource_id)
    def get(self):
        """获取所有项目类型"""
        staff = current_staff
        app = staff.app

        data = request.get_json()
        project = biz.create_project(app.id, data)
        return project, 201
