from flask_restplus import fields
from app.apis import api


_handling_session_item_specs = {
    'id': fields.Integer(readonly=True, description='session id'),
    'owner': fields.String(readonly=True),
    'updated': fields.DateTime(readonly=True, description='updated time')
}

handling_session_item = api.model('Handling Session Item', _handling_session_item_specs)
