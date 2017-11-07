from flask import request
from flask_restplus import Resource
from app.apis import logger
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
        msg = request.get_json()
        logger.debug('MsgNotify: %s', msg)
        kind = msg['kind']
        if kind == 'chat':
            tasks.sync_xchat_msgs.delay(msg)
        elif kind == 'chat_notify':
            tasks.notify_xchat_msgs.delay(msg)
        return None, 204
