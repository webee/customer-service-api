from flask_restplus import Resource, abort
from app.errors import BizError
from .api import api


@api.route('/')
class Test(Resource):
    def get(self):
        # abort(400)
        # raise BizError("test", "test", 406)
        return dict(test='OK')
