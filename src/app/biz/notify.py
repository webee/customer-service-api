import json
from app import xchat_client


class NotifyNS:
    PROJECT = 'project'


def notify_client(user, ns, type, details, domain=''):
    msg = json.dumps(dict(ns=ns, type=type, details=details))
    xchat_client.send_user_notify(user, msg, domain=domain)
