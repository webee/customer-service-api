from flask import request
from flask_restplus import Resource, abort
from app.apis import logger
from .api import api
from app.biz import app as biz
from app.apis.jwt import current_application, require_app
from .serializers import new_channel_message


@api.route('/projects/send_channel_msg')
class ChannelMessages(Resource):
    @require_app
    @api.expect(new_channel_message)
    @api.response(204, 'project is created')
    def post(self, id):
        """接收其它渠道的消息"""
        app = current_application
        data = request.get_json()
        proj = biz.get_project(app, data.get('project_id', data.get('project_domain'), data.get('project_type'), data.get('biz_id')))
        # TODO:
        logger.debug('SendChannelMessages: %s', data)
        return None, 204
