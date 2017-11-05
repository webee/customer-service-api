from flask import request
from flask_restplus import Resource
from .api import api
from .serializers import notified_msg
from app.task import tasks


@api.route('/msg_notify')
class MsgNotify(Resource):
    @api.expect(notified_msg)
    @api.response(204, 'received')
    @api.response(401, 'change password failed')
    def post(self):
        """接收消息通知"""
        data = request.get_json()
        kind = data['kind']
        if kind == 'chat':
            tasks.sync_xchat_msgs(data)
        elif kind == 'chat_notify':
            tasks.notify_xchat_msgs(data)
        return None, 204
