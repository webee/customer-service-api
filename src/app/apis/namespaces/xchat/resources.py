from flask import request
from flask_restplus import Resource
from app.apis import logger
from .api import api
from .serializers import notified_event, notified_msg, notified_user_status
from app.biz import xchat as xchat_biz


@api.route('/event_notify')
class EventNotify(Resource):
    @api.expect(notified_event)
    @api.response(204, 'received')
    @api.response(401, 'change password failed')
    def post(self):
        """接收事件通知"""
        data = request.get_json()
        logger.debug('EventNotify: %s', data)

        event = data.get('event')
        if event == 'msg':
            msg = data.get('data')
            # TODO: 使用schema校验
            xchat_biz.handle_msg_notify(msg)
        elif event == 'user_status':
            user_statuses = data.get('data')
            # TODO: 使用schema校验
            xchat_biz.handle_user_statuses(user_statuses)

        return None, 204
