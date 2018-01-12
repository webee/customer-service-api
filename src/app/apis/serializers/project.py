from flask_restplus import fields
from app import ma
from . import api
from . import base_resource, resource_id
from .app import path_label, data_item
from .staff import raw_staff, RawStaffSchema
from .customer import raw_customer, RawCustomerSchema

project = api.inherit('Project', resource_id, {
    'domain': fields.String(),
    'type': fields.String(),
    'biz_id': fields.String(),
    'tags': fields.List(fields.String),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer))
})

new_project = api.model('New Project', {
    'id': fields.Integer(required=False),
    'domain': fields.String(required=True, min_length=1, max_length=32),
    'type': fields.String(required=True, min_length=1, max_length=32),
    'biz_id': fields.String(required=True, min_length=1, max_length=32),
    'tags': fields.List(fields.String, default=[]),
    'start_msg_id': fields.Integer(required=False, min=0),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(data_item)),
    'scope_labels': fields.List(fields.Nested(path_label)),
    'class_labels': fields.List(fields.Nested(path_label))
})

update_project = api.model('Update Project', {
    'id': fields.Integer(),
    'domain': fields.String(),
    'type': fields.String(),
    'biz_id': fields.String(),
    'tags': fields.List(fields.String, default=[]),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(data_item)),
    'scope_labels': fields.List(fields.Nested(path_label)),
    'class_labels': fields.List(fields.Nested(path_label))
})

update_project_payload = api.model('Update Project Payload', {
    'tags': fields.List(fields.String, default=[]),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(data_item)),
    'scope_labels': fields.List(fields.Nested(path_label)),
    'class_labels': fields.List(fields.Nested(path_label))
})

project_data = api.model('Project Data', {
    'id': fields.Integer(description='project id'),
    'biz_id': fields.String(),
    'is_online': fields.Boolean(),
    'last_online_ts': fields.Float(attribute=lambda s: s.last_online_ts and s.last_online_ts.timestamp()),
    'tags': fields.List(fields.String),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(data_item)),
    'ext_data': fields.List(fields.Nested(data_item)),
    'current_session_id': fields.Integer(description='current session id')
})


class ProjectDataSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "biz_id", "is_online", "last_online_ts", "tags", "owner", "leader", "customers", "meta_data",
            "ext_data", "start_msg_id", "msg_id", "current_session_id")

    owner = ma.Nested(RawCustomerSchema)
    leader = ma.Nested(RawStaffSchema)
    customers = ma.List(ma.Nested(RawCustomerSchema))
    last_online_ts = ma.Function(lambda s: s.last_online_ts and s.last_online_ts.timestamp())


project_data_schema = ProjectDataSchema()

message = api.model('Message Result', {
    'channel': fields.String(),
    'user_type': fields.String(),
    'user_id': fields.String(),
    'tx_key': fields.Integer(),
    'rx_key': fields.Integer(),
    'msg_id': fields.Integer(),
    'domain': fields.String(),
    'type': fields.String(),
    'content': fields.String(),
    'ts': fields.Float(attribute=lambda msg: msg.ts.timestamp()),
    'session_id': fields.Integer(),
})

fetch_msgs_result = api.model('Fetch Msgs Result', {
    'msgs': fields.List(fields.Nested(message)),
    'has_more': fields.Boolean(description='has more msgs for this request?'),
    'no_more': fields.Boolean(description='no more msgs for this project?'),
})


class MessageSchema(ma.Schema):
    class Meta:
        fields = ("channel", "user_type", "user_id", "tx_key", "rx_key", "msg_id", "domain", "type", "content", "ts",
                  "session_id")

    ts = ma.Function(lambda msg: msg.ts.timestamp())


class FetchMsgsResultSchema(ma.Schema):
    class Meta:
        fields = ("msgs", "has_more", "no_more")

    msgs = ma.List(ma.Nested(MessageSchema))


fetch_msgs_result_schema = FetchMsgsResultSchema()


try_handle_project_result = api.model('Try Handle Project Result', {
    'domain': fields.String(),
    'type': fields.String(),
    'biz_id': fields.String(),
    'id': fields.Integer(),
    'current_session_id': fields.Integer()
})
