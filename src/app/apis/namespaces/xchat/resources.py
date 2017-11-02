from flask import request
from flask_restplus import Resource
from .api import api
from .serializers import notified_msg


@api.route('/msg_notify')
class MsgNotify(Resource):
    @api.expect(notified_msg)
    @api.response(204, 'received')
    @api.response(401, 'change password failed')
    def post(self):
        """接收消息通知"""
        data = request.get_json()
        print('notified msg: ', data)
        return None, 204
