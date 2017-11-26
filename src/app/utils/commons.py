def batch_split(list_data, batch_size=None):
    batch_size = batch_size or len(list_data)
    i = 0
    while i < len(list_data):
        j = i + batch_size
        yield list_data[i:j]
        i = j
