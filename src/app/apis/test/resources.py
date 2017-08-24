from flask_restplus import Resource
from .api import api


@api.route('/')
class Test(Resource):
    def get(self):
        return dict(test='OK')
