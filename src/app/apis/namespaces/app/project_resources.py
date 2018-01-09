from flask import request
from flask_restplus import Resource, abort
from sqlalchemy.orm.exc import NoResultFound
from app import dbs
from .api import api
from app import errors
from app.biz import app as biz
from app.biz import project as proj_biz
from app.biz.project import proj as proj_proj_biz
from app.apis.jwt import current_application, require_app
from app.apis.utils.xrestplus import marshal_with, marshal_list_with
from app.apis.serializers.project import project, new_project, update_project, update_project_payload
from app.apis.parsers.project import fetch_msgs_arguments
from app.apis.serializers.project import fetch_msgs_result, fetch_msgs_result_schema, try_handle_project_result
from .serializers import new_project_result
from .serializers import project_current_session_info
from .parsers import try_handle_project_arguments


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
        """批量更新项目信息: owner, customers, leader, meta_data, scope_labels, class_labels"""
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

        return proj

    @require_app
    @api.expect(update_project_payload)
    @api.response(404, 'project not found')
    @api.response(204, 'successfully updated')
    def patch(self, id=None, domain=None, type=None, biz_id=None):
        """更新项目信息: owner, customers, leader, meta_data, scope_labels, class_labels"""
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


@api.route('/projects/<int:id>/msgs',
           '/projects/<string:domain>/<string:type>/<string:biz_id>/msgs')
class ProjectMsgs(Resource):
    @require_app
    @api.expect(fetch_msgs_arguments)
    @api.doc(model=fetch_msgs_result)
    @marshal_with(fetch_msgs_result_schema)
    @api.response(404, 'project not found')
    @api.response(200, 'fetch msgs ok')
    def get(self, id, domain=None, type=None, biz_id=None):
        """获取项目消息"""
        app = current_application

        proj = biz.get_project(app, id, domain, type, biz_id)

        args = fetch_msgs_arguments.parse_args()
        lid = args['lid']
        rid = args['rid']
        limit = args['limit']
        desc = args['desc']
        msgs, has_more, no_more = proj_biz.fetch_project_msgs(proj, lid, rid, limit, desc)
        return dict(msgs=msgs, has_more=has_more, no_more=no_more)


@api.route('/projects/<int:id>/current_session',
           '/projects/<string:domain>/<string:type>/<string:biz_id>/current_session')
class ProjectCurrentSession(Resource):
    @require_app
    @api.marshal_with(project_current_session_info)
    @api.response(404, 'project not found')
    def get(self, id, domain=None, type=None, biz_id=None):
        """获取项目当前会话信息"""
        app = current_application

        proj = biz.get_project(app, id, domain, type, biz_id)
        current_session = proj.current_session
        if current_session is None:
            raise errors.BizError(errors.ERR_ITEM_NOT_FOUND, 'no current session', dict(id=proj.id))

        return current_session


@api.route('/projects/<int:id>/try_handle',
           '/projects/<string:domain>/<string:type>/<string:biz_id>/try_handle')
class TryHandleProject(Resource):
    @require_app
    @api.expect(try_handle_project_arguments)
    @api.marshal_with(try_handle_project_result)
    @api.response(404, 'project or staff not found')
    @api.response(200, 'try handle project ok')
    def get(self, id, domain=None, type=None, biz_id=None):
        """尝试接待项目"""
        app = current_application

        args = try_handle_project_arguments.parse_args()
        uid = args['uid']

        staff = app.staffs.filter_by(uid=uid).one()
        proj = biz.get_project(app, id, domain, type, biz_id)
        # 判断是否有权限
        if not proj_biz.staff_has_perm_for_project(staff, proj):
            raise errors.BizError(errors.ERR_PERMISSION_DENIED, 'staff can not handle this project',
                                  dict(uid=uid, id=proj.id))

        return proj_proj_biz.try_handle_project(proj, staff)
