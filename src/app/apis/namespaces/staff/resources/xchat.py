from flask import request
from flask_restplus import Resource, abort
from ..api import api
from app import config
from app.apis.jwt import current_staff, require_staff
from app.biz import xchat as xchat_biz


@api.route('/xchat')
class XChat(Resource):
    @require_staff
    def get(self):
        """获取xchat信息"""
        staff = current_staff
        ns = config.App.NAME
        name = staff.app_uid
        token, exp = xchat_biz.new_user_jwt(ns, name, config.XChat.DEFAULT_JWT_EXP_DELTA)
        return dict(ns=ns, app=staff.app.name,
                    name=name, username=xchat_biz.encode_ns_user(ns, name),
                    token=token, exp=exp,
                    ws_url=config.XChat.WS_URL)
