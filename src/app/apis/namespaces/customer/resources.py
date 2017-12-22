from flask import request
from flask_restplus import Resource, abort
from flask_restplus.marshalling import marshal
from .api import api
from app import config
from app.apis.jwt import current_customer, require_customer
from app.biz import xchat as xchat_biz
from app.biz import app as app_biz
from app.service.models import Project, UserType
from .serializers import app_customer, app_staff


@api.route('/xchat')
class XChat(Resource):
    @require_customer
    def get(self):
        """获取xchat信息"""
        customer = current_customer
        ns = config.App.NAME
        name = customer.app_uid
        token, exp = xchat_biz.new_user_jwt(ns, name, config.XChat.DEFAULT_JWT_EXP_DELTA)
        return dict(ns=ns, app=customer.app.name,
                    name=name, username=xchat_biz.encode_ns_user(ns, name),
                    token=token, exp=exp,
                    ws_url=config.XChat.WS_URL)


@api.route('/projects/<int:id>/xchat',
           '/projects/<string:domain>/<string:type>/<string:biz_id>/xchat')
class ProjectXChat(Resource):
    @require_customer
    @api.response(404, 'project not found.')
    def get(self, id=None, domain=None, type=None, biz_id=None):
        """获取project的xchat信息"""
        customer = current_customer
        app = customer.app

        proj = app_biz.get_user_project(app, customer, id, domain, type, biz_id)
        if proj is None:
            return abort(404, 'project not found')

        proj_xchat = proj.xchat
        return dict(chat_id=proj_xchat.chat_id)


@api.route('/users/xchat/<string:xchat_uid>',
           '/users/<string:user_type>/<string:uid>')
class AppUser(Resource):
    @require_customer
    @api.response(404, 'app user not found.')
    def get(self, user_type=None, uid=None, xchat_uid=None):
        """获取用户基本信息"""
        customer = current_customer
        app = customer.app

        if xchat_uid is not None:
            ns, app_uid = xchat_biz.decode_ns_user(xchat_uid)
            res, parts = app_biz.parse_app_uid(app_uid)
            if res:
                app_name, user_type, uid = parts
                if app_name != app.name:
                    return abort(404, 'app user not found')
            else:
                return abort(404, 'app user not found')

        if user_type is not None:
            if user_type == UserType.customer:
                customer = app.customers.filter_by(uid=uid).one()
                return marshal(customer, app_customer)
            elif user_type == UserType.staff:
                staff = app.staffs.filter_by(uid=uid).one()
                return marshal(staff, app_staff)
            return abort(404, 'app user not found')
        return abort(404, 'app user not found')
