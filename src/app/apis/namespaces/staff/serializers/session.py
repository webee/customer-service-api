from flask_restplus import fields
from app.apis import api


_new_message = {
    'domain': fields.String(default='', required=False, min_length=0, max_length=16),
    'type': fields.String(default='', required=False, min_length=0, max_length=24),
    'content': fields.String(required=True, min_length=1, max_length=64*1024),
}

new_message = api.model('New Message', _new_message)
