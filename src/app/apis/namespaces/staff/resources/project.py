from flask import request, abort
from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.service.models import Project, Session
from app.biz import project as proj_biz
from app.apis.utils.xrestplus import marshal_with, marshal_list_with
from ..parsers import fetch_msgs_arguments
from ..serializers.project import session_item, fetch_msgs_result, session_item_schema, fetch_msgs_result_schema


@api.route('/projects/<string:domain_name>/<string:type_name>/my_handling_sessions')
class MyHandlingSessions(Resource):
    @require_staff
    @marshal_list_with(session_item_schema, session_item)
    def get(self, domain_name, type_name):
        """获取我正在接待的会话"""
        staff = current_staff
        app = staff.app

        project_domain = app.project_domains.filter_by(name=domain_name).one()
        project_type = project_domain.types.filter_by(name=type_name).one()

        return staff.handling_sessions.filter(Project.type == project_type).all()


@api.route('/projects/<string:domain_name>/<string:type_name>/<int:session_id>')
class SessionItem(Resource):
    @require_staff
    @api.marshal_with(session_item)
    @api.response(404, 'session not found')
    def get(self, domain_name, type_name, session_id):
        """获取我正在接待的一个会话"""
        staff = current_staff
        app = staff.app

        project_domain = app.project_domains.filter_by(name=domain_name).one()
        project_type = project_domain.types.filter_by(name=type_name).one()

        return staff.handling_sessions.filter(Project.type == project_type).filter_by(id=session_id).one()


@api.route('/projects/<int:project_id>/msgs')
class ProjectMsgs(Resource):
    @require_staff
    @api.expect(fetch_msgs_arguments)
    @marshal_with(fetch_msgs_result_schema, fetch_msgs_result)
    @api.response(404, 'session not found')
    @api.response(200, 'fetch msgs ok')
    def get(self, project_id):
        """获取项目消息"""
        staff = current_staff

        proj = Project.query.filter_by(id=project_id).one()
        # FIXME: 添加权限控制
        if proj.app != staff.app:
            abort(404, 'session not found')

        args = fetch_msgs_arguments.parse_args()
        lid = args['lid']
        rid = args['rid']
        limit = args['limit']
        desc = args['desc']
        msgs, has_more = proj_biz.fetch_project_msgs(proj, lid, rid, limit, desc)
        return dict(msgs=msgs, has_more=has_more)
