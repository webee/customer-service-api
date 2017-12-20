from flask import request
from flask_restplus import Resource, abort
from .api import api
from app.biz import app as app_biz
from app import biz
from app.apis.jwt import current_application, require_app
from app.apis.serializers.app import update_application_payload
from app.apis.serializers.customer import raw_customer
from app.apis.serializers.staff import new_staff


@api.route('')
class App(Resource):
    @require_app
    @api.expect(update_application_payload)
    @api.response(204, 'successfully updated')
    def patch(self):
        """更新应用信息: appid, appkey, urls, access_functions, staff_label_tree"""
        app = current_application
        biz.update_app(app, request.get_json())
        return None, 204


# TODO:
# @api.route('/project_domain_types')
# class ProjectDomainTypeCollection(Resource):
#     @require_app
#     @api.expect([update_project_domain_type])
#     @api.response(204, 'successfully updated')
#     def patch(self):
#         """更新应用项目域类型的信息: access_functions, class_label_tree"""
#         app = current_application
#         return None, 204


@api.route('/customers')
class Customers(Resource):
    @require_app
    @api.expect([raw_customer])
    @api.response(204, 'created')
    def post(self):
        """批量创建或更新客户信息"""
        app = current_application
        data = request.get_json()

        app_biz.batch_create_or_update_customers(app, data)

        return None, 204


@api.route('/staffs')
class Staffs(Resource):
    @require_app
    @api.expect([new_staff])
    @api.response(204, 'created')
    def post(self):
        """批量创建或更新客服信息"""
        app = current_application
        data = request.get_json()

        app_biz.batch_create_or_update_staffs(app, data)

        return None, 204
