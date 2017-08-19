from flask import request, jsonify, abort
from flask.views import MethodView
from .entry import entry as mod
from app.service.test_models import Bucket


class BucketAPI(MethodView):
    def get(self, bucket_id=None):
        if bucket_id is None:
            buckets = Bucket.query.all()
            results = []

            for bucket in buckets:
                obj = {
                    'id': bucket.id,
                    'name': bucket.name,
                    'date_created': bucket.date_created,
                    'date_modified': bucket.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response
        else:
            bucket = Bucket.query.get(bucket_id)
            if bucket is None:
                abort(404)
            response = jsonify({
                'id': bucket.id,
                'name': bucket.name,
                'date_created': bucket.date_created,
                'date_modified': bucket.date_modified
            })
            response.status_code = 200
            return response

    def post(self):
        name = str(request.data.get('name', ''))
        if name:
            bucket = Bucket(name=name)
            bucket.save()
            response = jsonify({
                'id': bucket.id,
                'name': bucket.name,
                'date_created': bucket.date_created,
                'date_modified': bucket.date_modified
            })
            response.status_code = 201
            return response

    def patch(self, bucket_id):
        bucket = Bucket.query.get(bucket_id)
        if bucket is None:
            abort(404)

        name = str(request.data.get('name', ''))
        bucket.name = name
        bucket.save()
        response = jsonify({
            'id': bucket.id,
            'name': bucket.name,
            'date_created': bucket.date_created,
            'date_modified': bucket.date_modified
        })
        response.status_code = 200
        return response

    def delete(self, bucket_id):
        bucket = Bucket.query.get(bucket_id)
        if bucket is None:
            abort(404)

        bucket.delete()
        return {"message": "bucketlist {} deleted successfully".format(bucket.id)}, 200


bucket_view = BucketAPI.as_view('bucket_api')
mod.add_url_rule('/', defaults={'bucket_id': None}, view_func=bucket_view, methods=['GET'])
mod.add_url_rule('/', view_func=bucket_view, methods=['POST'])
mod.add_url_rule('/<int:bucket_id>', view_func=bucket_view, methods=['GET', 'PATCH', 'DELETE'])
