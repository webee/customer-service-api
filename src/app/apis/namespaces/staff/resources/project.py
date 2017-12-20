from flask import request, abort
from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.service.models import Project, Session
from app.biz import project as proj_biz
from app.apis.utils.xrestplus import marshal_with, marshal_list_with
from ..parsers import fetch_msgs_arguments
from ..serializers.project import session_item, fetch_msgs_result, session_item_schema, fetch_msgs_result_schema


@api.route('/projects/<string:domain>/<string:type>/my_handling_sessions')
class MyHandlingSessions(Resource):
    @require_staff
    @api.doc(model=session_item)
    @marshal_list_with(session_item_schema)
    def get(self, domain, type):
        """获取我正在接待的会话"""
        staff = current_staff

        return staff.handling_sessions.filter(Session.project.has(domain=domain, type=type)).all()


@api.route('/projects/<string:domain>/<string:type>/<int:id>')
class SessionItem(Resource):
    @require_staff
    @api.marshal_with(session_item)
    @api.response(404, 'session not found')
    def get(self, domain, type, id):
        """获取我正在接待的一个会话"""
        staff = current_staff

        return staff.handling_sessions.filter(Session.project.has(domain=domain, type=type)).filter_by(id=id).one()


@api.route('/projects/<int:id>/msgs')
class ProjectMsgs(Resource):
    @require_staff
    @api.expect(fetch_msgs_arguments)
    @api.doc(model=fetch_msgs_result)
    @marshal_with(fetch_msgs_result_schema)
    @api.response(404, 'session not found')
    @api.response(200, 'fetch msgs ok')
    def get(self, id):
        """获取项目消息"""
        staff = current_staff

        # FIXME: 添加权限控制
        proj = staff.app.projects.filter_by(id=id).one()

        args = fetch_msgs_arguments.parse_args()
        lid = args['lid']
        rid = args['rid']
        limit = args['limit']
        desc = args['desc']
        msgs, has_more = proj_biz.fetch_project_msgs(proj, lid, rid, limit, desc)
        return dict(msgs=msgs, has_more=has_more)
