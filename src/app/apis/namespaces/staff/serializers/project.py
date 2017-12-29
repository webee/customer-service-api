from flask_restplus import fields
from app.apis import api
from app.apis.serializers import pagination, PaginationSchema
from app.apis.serializers.project import project_data, ProjectDataSchema, MessageSchema, message
from app.apis.serializers.staff import raw_staff, RawStaffSchema
from app import ma

app_user = api.model('App User', {
    'uid': fields.String(),
    'name': fields.String(),
})

session_item = api.model('Session Item', {
    'id': fields.Integer(description='session id'),
    'project': fields.Nested(project_data),
    'created': fields.Float(attribute=lambda s: s.created.timestamp()),
    'closed': fields.Float(attribute=lambda s: s.closed and s.closed.timestamp()),
    'handler': fields.Nested(raw_staff),
    'start_msg_id': fields.Integer(description='start msg id'),
    'msg_id': fields.Integer(description='last msg id'),
    'msg': fields.Nested(message, allow_null=True, description='last msg'),
    'sync_msg_id': fields.Integer(description='synced msg id'),
    'handler_msg_id': fields.Integer(descripton="handler's last msg id"),
})


class SessionItemSchema(ma.Schema):
    class Meta:
        fields = (
            'id', 'project', 'created', 'closed', 'handler', 'start_msg_id', 'msg_id', 'msg', 'sync_msg_id',
            'handler_msg_id')

    project = ma.Nested(ProjectDataSchema)
    created = ma.Function(lambda s: s.created.timestamp())
    closed = ma.Function(lambda s: s.closed and s.closed.timestamp())
    handler = ma.Nested(RawStaffSchema)
    msg = ma.Nested(MessageSchema)


session_item_schema = SessionItemSchema()

page_of_sessions = api.inherit('Page of Sessions', pagination, {
    'items': fields.List(fields.Nested(session_item))
})


class PageOfSessionsSchema(PaginationSchema):
    items = ma.List(ma.Nested(SessionItemSchema))


page_of_sessions_schema = PageOfSessionsSchema()
