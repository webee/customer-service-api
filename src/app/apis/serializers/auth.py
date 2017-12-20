from flask_restplus import fields
from . import api


token_data = api.model('Token data', {
    'token': fields.String(readonly=True, descrption='jwt'),
    'exp': fields.Float(description='token expire ts')
})
