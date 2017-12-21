from .utils import normalize_data


def update_meta_data(user, data):
    meta_data = normalize_data(data)
    user.update_meta_data(meta_data)
