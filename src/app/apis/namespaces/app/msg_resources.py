import json
from flask import request
from flask_restplus import Resource, abort
from app import errors
from .api import api
from app.biz import app as biz
from app.biz import project as proj_biz
from app.apis.jwt import current_application, require_app
from .serializers import new_channel_message


@api.route('/projects/send_channel_msg')
class ChannelMessages(Resource):
    @require_app
    @api.expect(new_channel_message)
    @api.response(200, 'send msg successfully')
    def post(self):
        """转发其它渠道的消息到客服系统"""
        app = current_application
        data = request.get_json()
        proj = biz.get_project(app, data.get('project_id', data.get('id')), data.get('project_domain'),
                               data.get('project_type'), data.get('project_biz_id', data.get('biz_id')))

        uid = data['uid']
        try:
            customer = next(filter(lambda c: c.uid == uid, proj.customers))
        except StopIteration:
            raise errors.BizError(errors.ERR_PERMISSION_DENIED, 'customer is not the member of the project', dict(uid=uid))

        content = data['content']
        if isinstance(content, dict):
            content = json.dumps(content)

        rx_key, ts = proj_biz.send_channel_message(proj, customer, data['channel'], data.get('domain', ''), data['type'], content)
        return dict(rx_key=rx_key, ts=ts), 200
