from functools import wraps
from .path_labels import LabelType

LABEL_TYPE_MAP = {
    'up': LabelType.UP,
    'up+': LabelType.SUPER,
    'super': LabelType.SUPER,
    'self': LabelType.SELF,
    'self.': LabelType.MEMBER,
    'member': LabelType.MEMBER,
    'sub': LabelType.SUB,
    'self+': LabelType.SELF_PLUS,
    'self++': LabelType.SELF_PLUS_PLUS,
    'member+': LabelType.MEMBER_PLUS,
    'all': LabelType.ALL
}

CONTEXT_LABEL_TYPE_MAP = {
    'self': LabelType.SELF,
    'self.': LabelType.MEMBER,
    'member': LabelType.MEMBER,
    'self+': LabelType.SELF_PLUS
}


def normalize_labels(labels, type_map=LABEL_TYPE_MAP):
    if labels:
        return [[type_map[l[0]], l[1]] if isinstance(l, list) else [type_map[l['type']], l['path']]
                for l in labels]
    return labels


def normalize_context_labels(labels):
    return normalize_labels(labels, type_map=CONTEXT_LABEL_TYPE_MAP)


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
