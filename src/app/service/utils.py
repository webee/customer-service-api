from functools import wraps
from .path_labels import LabelType
from .path_labels import ctx_label_key

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

NULL_LABELS = [[None, None]]


def normalize_labels(labels, type_map=LABEL_TYPE_MAP):
    if labels == NULL_LABELS:
        return None
    if labels:
        return [[type_map[l[0]], l[1]] if isinstance(l, list) else [type_map[l['type']], l['path']]
                for l in labels]
    return labels


def normalize_context_labels(labels):
    if labels == NULL_LABELS:
        return None
    return sorted(normalize_labels(labels, type_map=CONTEXT_LABEL_TYPE_MAP), key=ctx_label_key)


def _get_alias_to(label):
    alias_to = label.get('alias_to')
    if alias_to is None:
        return {}
    return dict(alias_to=alias_to)


def _normalize_label(label):
    if label.get('children'):
        return {'name': label['name'], 'children': normalize_label_tree(label['children']), **_get_alias_to(label)}

    return {'name': label['name'], **_get_alias_to(label)}


def normalize_label_tree(label_tree):
    if isinstance(label_tree, dict):
        return {code: _normalize_label(label) for code, label in label_tree.items()}
    return {label['code']: _normalize_label(label) for label in label_tree}


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
