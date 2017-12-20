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


def normalize_data(data):
    if data:
        return [d if isinstance(d, list) else [d['label'], d.get('type', 'value'), d['value']] for d in data]
    return data
