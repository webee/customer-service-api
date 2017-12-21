from flask_restplus import Resource, abort
from app.utils.app_client.constant import ErrorCode
import random
from .api import api
from . import resp
from .auth import auth_required, encode_token
from .parsers import auth_args, get_ext_data_args, access_function_args
from .serializers import new_msg


@api.route('/getToken')
class Gettoken(Resource):
    @api.expect(auth_args)
    def get(self):
        try:
            return resp.success(encode_token())
        except:
            return resp.fail(ErrorCode.AUTH_FAILED, '认证失败')


@api.route('/getExtData')
class GetExtData(Resource):
    @auth_required
    @api.expect(get_ext_data_args)
    def get(self):
        # args = get_ext_data_args.parse_args()
        data = [{
            'label': '数据#%d' % x,
            'type': ('value', 'link')[x],
            'value': ('数据值[%d]' % i, {"value": "链接<%d>" % i, "href": "https://www.baidu.com/"})[x]
        } for i, x in enumerate([random.randint(0, 1) for i in range(random.randint(2, 6))])]
        return resp.success(data)


@api.route('/accessFunction')
class AccessFunction(Resource):
    @auth_required
    @api.expect(access_function_args)
    def get(self):
        args = access_function_args.parse_args()
        return resp.success(args)


@api.route('/sendChannelMsg')
class SendChannelMsg(Resource):
    @auth_required
    @api.expect(new_msg)
    def post(self):
        return resp.success()
