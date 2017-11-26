from flask import request
from flask_restplus import Resource, abort
from ..api import api
from app.apis.jwt import current_staff, require_staff
from ..serializers.session import new_message, sync_msg_id
from app.biz import project as proj_biz


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

