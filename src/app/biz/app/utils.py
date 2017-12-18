def normalize_labels(labels):
    if labels:
        return [l if isinstance(l, list) else [l['type'], l['path']] for l in labels]
    return labels


def normalize_data(data):
    if data:
        return [d if isinstance(d, list) else [d['label'], d.get('type', 'value'), d['value']] for d in data]
    return data
