from flask import request
from flask_restplus import Resource
from .api import api
from . import serializers as ser
from ..serializers import resource_id
from app.biz import app as biz
from ..jwt import current_app_client, require_app


@api.route('/sessions')
class SessionCollection(Resource):
    """会话相关"""
    @require_app
    # @api.expect(raw_project)
    @api.marshal_with(resource_id)
    def post(self):
        """创建项目"""
        app = current_app_client
        data = request.get_json()
        project = biz.create_project(app.id, data)
        return project, 201
