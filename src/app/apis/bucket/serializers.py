from flask_restplus import fields
from .. import api
from ..serializers import pagination, base_resource

_raw_bucket_specs = {
    'name': fields.String(required=True, min_length=1, description='bucket name')
}

raw_bucket = api.model('Raw Bucket', _raw_bucket_specs)
bucket = api.inherit('Bucket', base_resource, _raw_bucket_specs)

page_of_buckets = api.inherit('Page of buckets', pagination, {
    'items': fields.List(fields.Nested(bucket))
})
