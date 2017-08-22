from .entry import entry as mod


@mod.route('/')
def index():
    return "OK"
