from flask_restplus import Namespace

name = __package__.rsplit('.', 1)[1]
api = Namespace(name, description='%s description' % name)
