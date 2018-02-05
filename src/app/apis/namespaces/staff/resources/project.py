from flask import request, abort
from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.service.models import Project, Session
from app.biz import project as proj_biz
from app.biz.project import proj as proj_proj_biz
from app.biz import session as session_biz
from app import app_clients
from app import errors
from app.apis.utils.xrestplus import marshal_with, marshal_list_with
from app.apis.parsers.project import fetch_msgs_arguments
from app.apis.serializers.project import fetch_msgs_result, fetch_msgs_result_schema, project_data, project_data_schema, try_handle_project_result
from ..parsers import access_function_args, fetch_handling_sessions_args, fetch_handled_sessions_args
from ..serializers.project import session_item, session_item_schema, page_of_sessions, page_of_sessions_schema


@api.route('/projects/<string:domain>/<string:type>/my_handling_sessions')
class MyHandlingSessions(Resource):
    @require_staff
    @api.doc(model=session_item)
    @marshal_list_with(session_item_schema)
    def get(self, domain, type):
        """获取我正在接待的会话"""
        staff = current_staff

        return staff.handling_sessions.filter(Session.project.has(domain=domain, type=type)).all()


@api.route('/projects/<string:domain>/<string:type>/handling_sessions')
class HandlingSessions(Resource):
    @require_staff
    @api.expect(fetch_handling_sessions_args)
    @api.doc(model=page_of_sessions)
    @marshal_with(page_of_sessions_schema)
    def get(self, domain, type):
        """获取正在接待中的会话列表"""
        staff = current_staff
        app = staff.app

        args = fetch_handling_sessions_args.parse_args()

        return session_biz.staff_fetch_handling_sessions(app, staff, domain, type, **args)


@api.route('/projects/<string:domain>/<string:type>/handled_sessions')
class HandledSessions(Resource):
    @require_staff
    @api.expect(fetch_handled_sessions_args)
    @api.doc(model=page_of_sessions)
    @marshal_with(page_of_sessions_schema)
    def get(self, domain, type):
        """获取已经完成接待的会话列表"""
        staff = current_staff
        app = staff.app

        args = fetch_handled_sessions_args.parse_args()

        return session_biz.staff_fetch_handled_sessions(app, staff, domain, type, **args)


@api.route('/sessions/<int:id>')
class SessionItem(Resource):
    @require_staff
    @api.doc(model=session_item)
    @marshal_with(session_item_schema)
    @api.response(404, 'session not found')
    def get(self, id):
        """获取我正在接待的一个会话"""
        staff = current_staff

        return staff.handling_sessions.filter_by(id=id).one()


@api.route('/projects/<int:id>')
class ProjectItem(Resource):
    @require_staff
    @api.doc(model=project_data)
    @marshal_with(project_data_schema)
    @api.response(404, 'project not found')
    def get(self, id):
        """获取项目数据"""
        staff = current_staff

        return proj_biz.get_staff_project(staff, id)


@api.route('/projects/<int:id>/msgs')
class ProjectMsgs(Resource):
    @require_staff
    @api.expect(fetch_msgs_arguments)
    @api.doc(model=fetch_msgs_result)
    @marshal_with(fetch_msgs_result_schema)
    @api.response(404, 'project not found')
    @api.response(200, 'fetch msgs ok')
    def get(self, id):
        """获取项目消息"""
        staff = current_staff

        proj = staff.app.projects.filter_by(id=id).one()
        # 判断是否有权限
        if not proj_biz.staff_has_perm_for_project(staff, proj):
            raise errors.BizError(errors.ERR_PERMISSION_DENIED, 'staff has no permission for this project',
                                  dict(uid=staff.uid, id=proj.id))

        args = fetch_msgs_arguments.parse_args()
        msgs, has_more, no_more = proj_biz.fetch_project_msgs(proj, **args)
        return dict(msgs=msgs, has_more=has_more, no_more=no_more)


@api.route('/projects/<int:id>/access_functions/<name>/url')
class ProjectAccessFunctionURL(Resource):
    @require_staff
    @api.expect(access_function_args)
    @api.response(404, 'project not found')
    def get(self, id, name):
        """访问项目功能"""
        staff = current_staff

        proj = staff.app.projects.filter_by(id=id).one()
        # 判断是否有权限
        if not proj_biz.staff_has_perm_for_project(staff, proj):
            raise errors.BizError(errors.ERR_PERMISSION_DENIED, 'staff has no permission for this project',
                                  dict(uid=staff.uid, id=proj.id))

        args = access_function_args.parse_args()
        uid = args.get('uid')
        if uid and not (uid == proj.owner.uid or any(c.uid == uid for c in proj.customers)):
            # 指定的uid不是owner也不是customers
            raise errors.BizError(errors.ERR_INVALID_PARAMS, 'invalid uid', dict(uid=uid))
        elif not uid:
            uid = proj.owner.uid

        app = staff.app
        app_client = app_clients.get_client(app.appid, app.appkey, app.urls)
        url = app_client.build_access_function_url(proj.domain, proj.type, proj.biz_id, proj.owner.uid, name,
                                                   id=proj.id, uid=uid)

        return dict(url=url)


@api.route('/projects/<int:id>/fetch_ext_data')
class ProjectFetchExtData(Resource):
    @require_staff
    @api.response(204, 'fetch ext data started successfully')
    def get(self, id):
        """获取项目扩展数据"""
        staff = current_staff

        proj = staff.app.projects.filter_by(id=id).one()
        # 判断是否有权限
        if not proj_biz.staff_has_perm_for_project(staff, proj):
            raise errors.BizError(errors.ERR_PERMISSION_DENIED, 'staff has no permission for this project',
                                  dict(uid=staff.uid, id=proj.id))

        proj_biz.fetch_ext_data(staff, proj)
        return None, 204


@api.route('/projects/<int:id>/try_handle')
class TryHandleProject(Resource):
    @require_staff
    @api.marshal_with(try_handle_project_result)
    @api.response(200, 'try handle project ok')
    def get(self, id):
        """尝试接待项目"""
        staff = current_staff

        proj = staff.app.projects.filter_by(id=id).one()
        # 判断是否有权限
        if not proj_biz.staff_has_perm_for_project(staff, proj):
            raise errors.BizError(errors.ERR_PERMISSION_DENIED, 'can not handle this project',
                                  dict(uid=staff.uid, id=proj.id))

        return proj_proj_biz.try_handle_project(proj, staff)
