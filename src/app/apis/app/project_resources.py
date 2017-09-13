from flask import request
from flask_restplus import Resource
from .api import api
from .serializers import raw_project, raw_project_customers, raw_project_staffs
from . import serializers as ser
from ..serializers import resource_id
from app.biz import app as biz
from ..jwt import current_app_client, require_app


@api.route('/projects')
class ProjectCollection(Resource):
    """项目相关"""
    @require_app
    @api.expect(ser.raw_project)
    @api.marshal_with(resource_id)
    def post(self):
        """创建项目"""
        app = current_app_client
        data = request.get_json()
        project = biz.create_project(app.id, data)
        return project, 201


@api.route('/projects/<int:id>')
class ProjectItem(Resource):
    """项目相关"""
    @require_app
    @api.marshal_with(ser.project)
    @api.response(404, 'project not found')
    def get(self, id):
        """获取项目"""
        app = current_app_client
        return app.projects.filter_by(id=id).one()


@api.route('/projects/<int:id>/customers')
class ProjectCustomers(Resource):
    @require_app
    @api.expect(raw_project_customers)
    @api.response(204, 'successfully added')
    def post(self, id):
        """添加项目客户"""
        app = current_app_client
        project = app.projects.filter_by(id=id).one()
        data = request.get_json()
        # TODO
        return None, 204

    @require_app
    @api.expect(raw_project_customers)
    @api.response(204, 'successfully deleted')
    def delete(self, id):
        """删除项目客户"""
        app = current_app_client
        project = app.projects.filter_by(id=id).one()
        data = request.get_json()
        # TODO
        return None, 204

    @require_app
    @api.expect(raw_project_customers)
    @api.response(204, 'successfully replaced')
    def put(self, id):
        """替换项目客户"""
        app = current_app_client
        project = app.projects.filter_by(id=id).one()
        data = request.get_json()
        # TODO
        return None, 204


@api.route('/projects/<int:id>/staffs')
class ProjectStaffs(Resource):
    @require_app
    @api.expect(raw_project_staffs)
    @api.response(204, 'successfully replaced')
    def put(self, id):
        """替换项目客服"""
        app = current_app_client
        project = app.projects.filter_by(id=id).one()
        data = request.get_json()
        # TODO
        return None, 204

    @require_app
    @api.expect(raw_project_staffs)
    @api.response(204, 'successfully updated')
    def patch(self, id):
        """更新项目客服"""
        app = current_app_client
        project = app.projects.filter_by(id=id).one()
        data = request.get_json()
        # TODO
        return None, 204
