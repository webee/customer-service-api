from app import db
from app.service.test_models import Bucket


def create_bucket(data):
    name = data.get('name')
    bucket = Bucket(name)
    db.session.add(bucket)
    db.session.commit()

    return bucket


def update_bucket(id, data):
    bucket = Bucket.query.get_or_404(id)
    bucket.name = data.get('name')
    db.session.add(bucket)
    db.session.commit()


def delete_bucket(id):
    bucket = Bucket.query.get_or_404(id)
    db.session.delete(bucket)
    db.session.commit()
