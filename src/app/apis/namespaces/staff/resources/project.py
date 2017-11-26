from flask import request, abort
from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.service.models import Project, Session
from app.biz import project as proj_biz
from ..parsers import fetch_msgs_arguments
from ..serializers.project import handling_session_item, fetch_msgs_result


@api.route('/projects/<string:domain_name>/<string:type_name>/my_handling_sessions')
class MyHandlingSessions(Resource):
    @require_staff
    @api.marshal_list_with(handling_session_item)
    def get(self, domain_name, type_name):
        """获取我正在接待的会话"""
        staff = current_staff
        app = staff.app

        project_domain = app.project_domains.filter_by(name=domain_name).one()
        project_type = project_domain.types.filter_by(name=type_name).one()

        return staff.handling_sessions.filter(Project.type == project_type).all()


@api.route('/sessions/<int:project_id>/msgs')
class SessionMsgs(Resource):
    @require_staff
    @api.expect(fetch_msgs_arguments)
    @api.marshal_with(fetch_msgs_result)
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
