from app.utils import resp
from .entry import entry as mod


@mod.route('/')
def index():
    return resp.success()
