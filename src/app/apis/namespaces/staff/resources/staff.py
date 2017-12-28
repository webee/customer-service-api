from flask import request, abort
from flask_restplus import Resource
from ..api import api
from app.apis.jwt import current_staff, require_staff
from app.biz import staff as biz
from ..parsers import fetch_staffs_args
from ..serializers.staff import page_of_staffs


@api.route('/staffs')
class Staffs(Resource):
    @require_staff
    @api.expect(fetch_staffs_args)
    @api.marshal_with(page_of_staffs)
    def get(self):
        """获取客服列表"""
        staff = current_staff
        app = staff.app

        args = fetch_staffs_args.parse_args()
        page = args['page']
        per_page = args['per_page']
        name = args['name']
        uid = args['uid']
        context_label = args['context_label']
        is_online = args['is_online']
        is_deleted = args['is_deleted']
        sorter = args['sorter']
        order = args['order']

        return biz.staff_fetch_staffs(app, staff, page, per_page, name=name, uid=uid, context_label=context_label, is_online=is_online, is_deleted=is_deleted,
                                sorter=sorter, order=order)
