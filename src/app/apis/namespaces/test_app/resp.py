def success(data=None):
    return dict(ret=True, data=data)


def fail(error_code, error_msg):
    return dict(ret=False, error_code=error_code, error_msg=error_msg)
