from .utils import normalize_data, normalize_labels


def update_scope_labels(proj, data):
    scope_labels = normalize_labels(data)
    proj.update_scope_labels(scope_labels)


def update_class_labels(proj, data):
    class_labels = normalize_labels(data)
    proj.update_class_labels(class_labels)


def update_meta_data(proj, data):
    meta_data = normalize_data(data)
    proj.update_meta_data(meta_data)


def update_ext_data(proj, data):
    ext_data = normalize_data(data)
    proj.update_ext_data(ext_data)
