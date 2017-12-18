from flask import request
from flask_restplus import Resource, abort
from sqlalchemy.orm.exc import NoResultFound
from app import dbs
from .api import api
from app.biz import app as biz
from app.apis.jwt import current_application, require_app
from app.apis.serializers.project import project, new_project, update_project, update_project_payload, meta_data_item
from .serializers import new_project_result


@api.route('/projects')
class ProjectCollection(Resource):
    """项目相关"""

    @require_app
    @api.expect(new_project)
    @api.marshal_with(new_project_result)
    @api.response(201, 'project is created')
    def post(self):
        """创建项目"""
        app = current_application
        project = biz.create_project(app, request.get_json())
        # NOTE: return project_id and xchat chat_id
        # 给后端和app端两个选择，要么后端返回chat_id, 要么app使用project_id查询cs的接口获取chat_id
        return project, 201

    @require_app
    @api.expect([new_project])
    @api.marshal_list_with(new_project_result)
    @api.response(201, 'project is created')
    def put(self):
        """批量创建项目"""
        app = current_application
        projects = biz.batch_create_projects(app, request.get_json())
        return projects, 201

    @require_app
    @api.expect([update_project])
    @api.response(204, 'successfully updated')
    def patch(self):
        """批量更新项目信息: owner, customers, leader, meta_data, scope_labels"""
        app = current_application
        biz.batch_update_projects(app, request.get_json())
        return None, 204


@api.route('/projects/<int:id>',
           '/projects/<string:domain>/<string:type>/<string:biz_id>')
class ProjectItem(Resource):
    @require_app
    @api.marshal_with(project)
    @api.response(404, 'project not found')
    def get(self, id=None, domain=None, type=None, biz_id=None):
        """获取项目"""
        app = current_application
        proj = biz.get_project(app, id, domain, type, biz_id)
        if proj is None:
            return abort(404, 'project not found')

        return proj

    @require_app
    @api.expect(update_project_payload)
    @api.response(204, 'successfully updated')
    def patch(self, id=None, domain=None, type=None, biz_id=None):
        """更新项目信息: owner, customers, leader, meta_data, scope_labels"""
        app = current_application
        proj = biz.get_project(app, id, domain, type, biz_id)
        biz.update_project(proj, request.get_json())
        return None, 204


@api.route('/projects/<int:id>/is_exists',
           '/projects/<string:domain>/<string:type>/<string:biz_id>/is_exists')
class IsProjectItemExists(Resource):
    @require_app
    def get(self, id=None, domain=None, type=None, biz_id=None):
        """检查项目是否存在"""
        app = current_application

        is_exists = biz.is_project_exists(app, id, domain, type, biz_id)
        return dict(is_exists=is_exists)
