from functools import wraps

LABEL_TYPE_MAP = {
    'super': str(0b10),
    'self': str(0b00),
    'sub': str(0b01),
    'all': str(0b11),
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
            return fn(self, arg)

    return wrap
