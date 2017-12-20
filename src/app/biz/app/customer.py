from app import dbs
from .utils import normalize_data


@dbs.transactional
def update_meta_data(user, data):
    meta_data = normalize_data(data)
    user.update_meta_data(meta_data)
