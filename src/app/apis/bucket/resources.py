from flask import request
from flask_restplus import Resource
from app.service.test_models import Bucket
from .api import api
from ..parsers import pagination_arguments
from ..serializers import resource_id
from .serializers import page_of_buckets, raw_bucket, bucket
from app.biz import bucket as biz


@api.route('/')
class BucketCollection(Resource):
    @api.expect(pagination_arguments)
    @api.marshal_with(page_of_buckets)
    def get(self):
        """get list of buckets.
        """
        args = pagination_arguments.parse_args()
        page = args['page']
        per_page = args['per_page']

        bucket_page = Bucket.query.paginate(page, per_page, error_out=False)

        return bucket_page

    @api.expect(raw_bucket)
    @api.marshal_with(bucket, mask='id')
    def post(self):
        """create a new bucket.
        """
        return biz.create_bucket(request.get_json()), 201


@api.route('/<int:id>')
@api.response(404, 'Bucket not found.')
class BucketItem(Resource):
    @api.marshal_with(bucket)
    def get(self, id):
        """get a bucket.
        """
        return Bucket.query.get(id)

    @api.response(204, 'Bucket successfully updated.')
    def patch(self, id):
        """update a bucket.
        """
        return biz.update_bucket(id, request.get_json()), 204

    @api.response(204, 'Bucket successfully deleted.')
    def delete(self, id):
        """delete a bucket.
        """
        return biz.delete_bucket(id), 204
