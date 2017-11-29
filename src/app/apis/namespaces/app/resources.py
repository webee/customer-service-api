from flask import request
from flask_restplus import Resource, abort
from .api import api
from app.biz import app as biz
from app.apis.jwt import current_application, require_app
from app.apis.serializers.customer import raw_customer
from app.apis.serializers.staff import raw_staff


@api.route('/customers')
class Customers(Resource):
    @require_app
    @api.expect([raw_customer])
    @api.response(204, 'created')
    def post(self):
        """批量创建客户"""
        app = current_application
        data = request.get_json()

        biz.batch_create_or_update_customers(app, data)

        return None, 204


@api.route('/staffs')
class Staffs(Resource):
    @require_app
    @api.expect([raw_staff])
    @api.response(204, 'created')
    def post(self):
        """批量创建客服"""
        app = current_application
        data = request.get_json()

        biz.batch_create_or_update_staffs(app, data)

        return None, 204
