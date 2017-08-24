from app import db
from .model_commons import BaseModel


class Bucket(BaseModel):
    """This class represents the bucket table."""
    __tablename__ = 'bucket'

    name = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self, name):
        """initialize with name."""
        self.name = name

    def __repr__(self):
        return "<Bucket: {}>".format(self.name)
