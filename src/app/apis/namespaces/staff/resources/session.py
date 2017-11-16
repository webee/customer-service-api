from flask import request
from flask_restplus import Resource, abort
from ..api import api
from app.apis.jwt import current_staff, require_staff
from ..serializers.session import new_message, sync_msg_id, fetch_msgs_result
from ..parsers import fetch_msgs_arguments
from app.biz import project as proj_biz
from app.service.models import Session


@api.route('/sessions/<int:project_id>/<int:session_id>/send_msg')
class SessionSendMsg(Resource):
    @require_staff
    @api.expect(new_message)
    @api.response(403, 'you are not the session handler')
    @api.response(403, 'session is not active')
    @api.response(204, 'send msg successfully')
    def post(self, project_id, session_id):
        """发送消息"""
        staff = current_staff

        session = staff.get_handling_session(session_id)
        if session is None:
            abort(403, 'you are not the session handler')
        if not session.is_active:
            abort(403, 'session is not active')

        data = request.get_json()
        proj_biz.send_message(staff, session, data.get('domain', ''), data.get('type', ''), data['content'])
        return None, 204


@api.route('/sessions/<int:project_id>/<int:session_id>/sync_msg_id')
class SyncSessionMsgID(Resource):
    @require_staff
    @api.expect(sync_msg_id)
    @api.response(403, 'you are not the session handler')
    @api.response(403, 'session is not active')
    @api.response(204, 'sync msg id successfully')
    def post(self, project_id, session_id):
        """同步会话消息id"""
        staff = current_staff

        session = staff.get_handling_session(session_id)
        if session is None:
            abort(403, 'you are not the session handler')
        if not session.is_active:
            abort(403, 'session is not active')

        data = request.get_json()
        proj_biz.sync_session_msg_id(staff, session, data.get('msg_id', 0))
        return None, 204


@api.route('/sessions/<int:project_id>/<int:session_id>/msgs')
class SessionMsgs(Resource):
    @require_staff
    @api.expect(fetch_msgs_arguments)
    @api.marshal_with(fetch_msgs_result)
    @api.response(404, 'session not found')
    @api.response(200, 'fetch msgs ok')
    def get(self, project_id, session_id):
        """获取会话消息"""
        staff = current_staff

        # FIXME: 添加权限控制
        session = Session.query.filter_by(id=session_id).one()
        if session.project.app != staff.app:
            abort(404, 'session not found')

        args = fetch_msgs_arguments.parse_args()
        lid = args['lid']
        rid = args['rid']
        limit = args['limit']
        desc = args['desc']
        msgs, has_more = proj_biz.fetch_session_msgs(session, lid, rid, limit, desc)
        return dict(msgs=msgs, has_more=has_more)
