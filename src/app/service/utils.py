from functools import wraps
from .path_labels import LT_SUPER, LT_SELF, LT_SUB, LT_ALL

LABEL_TYPE_MAP = {
    'super': LT_SUPER,
    'self': LT_SELF,
    'sub': LT_SUB,
    'all': LT_ALL,
}


def normalize_labels(labels):
    if labels:
        return [[LABEL_TYPE_MAP[l[0]], l[1]] if isinstance(l, list) else [LABEL_TYPE_MAP[l['type']], l['path']]
                for l in labels]
    return labels


def normalize_label_tree(label_tree):
    if isinstance(label_tree, dict):
        return {code: {'name': label['name'], 'children': normalize_label_tree(label['children'])}
        if label.get('children') else {'name': label['name']}
                for code, label in label_tree.items()}
    return {label['code']: {
        'name': label['name'], 'children': normalize_label_tree(label['children'])} if label.get('children') else {
        'name': label['name']} for label in label_tree}


def normalize_data(data):
    if data:
        return [d if isinstance(d, list) else [d['label'], d.get('type', 'value'), d['value']] for d in data]
    return data


def ignore_none(fn):
    @wraps(fn)
    def wrap(self, arg):
        if arg is not None:
            return fn(self, arg) or True

    return wrap
