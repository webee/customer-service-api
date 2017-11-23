import json
from flask_restplus import Resource, abort
from app import errors
from app.errors import BizError
from .api import api


@api.route('/')
class Test(Resource):
    def get(self):
        return dict(test='OK', ns='test', path='/'), 200, {'cs-api-xxx': json.dumps(dict(ns='test', path='/'))}


@api.route('/abort')
class TestAbort(Resource):
    def get(self):
        abort(400, 'test abort 400', custom=dict(ns='test', path='/abort'))


@api.route('/biz_error')
class TestBizError(Resource):
    def get(self):
        raise BizError(errors.ERR_XXX, 'what ever xxx', dict(ns='test', path='/biz_error'))
