import functools


def batch_split(list_data, batch_size=None):
    batch_size = batch_size or len(list_data)
    i = 0
    while i < len(list_data):
        j = i + batch_size
        yield list_data[i:j]
        i = j


def merge_to_dict(d, **kwargs):
    res = dict(d)
    res.update(kwargs)
    return res


def compose(f, *funcs):
    return functools.reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)), funcs, f)
