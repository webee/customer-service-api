from flask_restplus import fields
from app.apis import api
from app.apis.serializers import pagination
from app.apis.serializers.xfields import any_of

staff_data = api.model('Staff Data', {
    'uid': fields.String(),
    'name': fields.String(),
    'context_labels': any_of(['array']),
    'is_online': fields.Boolean(),
    'is_deleted': fields.Boolean(),
    'last_online_ts': fields.Float(attribute=lambda s: s.last_online_ts and s.last_online_ts.timestamp()),
    'created': fields.Float(attribute=lambda x: x.created.timestamp()),
    'updated': fields.Float(attribute=lambda x: x.updated.timestamp()),
})

page_of_staffs = api.inherit('Page of Staffs', pagination, {
    'items': fields.List(fields.Nested(staff_data))
})
