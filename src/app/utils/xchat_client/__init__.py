import os
import threading
import requests
import jwt
from datetime import datetime, timedelta
from pytoolbox.util import pmc_config
from .config import Config
from . import constant


class RequestResult(object):
    def __init__(self, resp):
        self.resp = resp
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.resp.json()
        return self._data

    def is_success(self):
        return 200 <= self.resp.status_code < 300


class RequestError(Exception):
    """http请求错误"""
    def __init__(self, resp):
        self.resp = resp
        super().__init__('request error: %d' % self.resp.status_code)


class RequestFailedError(Exception):
    """请求执行失败"""
    def __init__(self, msg):
        super().__init__(msg)


class XChatClient(object):
    constant = constant

    def __init__(self, env_config=None):
        self.config = Config()
        self._token = None
        self._token_exp = None
        self._lock = threading.RLock()

        if env_config is not None:
            self.init_config(env_config)

    def init_config(self, env_config):
        pmc_config.merge_config(self.config, env_config)

    def _new_token(self):
        exp = datetime.utcnow() + timedelta(days=30)
        payload = dict(
            ns='',
            is_admin=True,
            exp=exp
        )

        return jwt.encode(payload, self.config.USER_KEY).decode('utf-8'), exp

    def _is_current_token_valid(self):
        return self._token and self._token_exp > datetime.utcnow() + timedelta(minutes=30)

    @property
    def token(self):
        if not self._is_current_token_valid():
            with self._lock:
                if not self._is_current_token_valid():
                    self._token, self._token_exp = self._new_token()
        return self._token

    def _build_url(self, url, **kwargs):
        url = url.lstrip('/')
        return os.path.join(self.config.ROOT_URL, url.format(**kwargs))

    def _request(self, method, url, data=None, **kwargs):
        headers = {'Authorization': 'Bearer ' + self.token}
        resp = requests.request(method, url, json=data, headers=headers, **kwargs)
        return RequestResult(resp)

    def _get(self, url, **kwargs):
        return self._request('get', url, **kwargs)

    def _post(self, url, data=None, **kwargs):
        return self._request('post', url, data, **kwargs)

    def _put(self, url, data=None, **kwargs):
        return self._request('put', url, data, **kwargs)

    def _delete(self, url, data=None, **kwargs):
        return self._request('delete', url, data, **kwargs)

    def new_chat(self, type, users=(), biz_id=None, mq_topic=None, title=None, tag=None, ext=None):
        data = {'type': type, 'users': users}
        for k, v in {'biz_id': biz_id, 'mq_topic': mq_topic, 'title': title, 'tag': tag, 'ext': ext}.items():
            if v is not None:
                data[k] = v

        url = self._build_url(self.config.CHATS_URL)
        res = self._post(url, data)
        if res.is_success():
            return res.data['id']

    def get_chat(self, chat_id):
        url = self._build_url(self.config.CHAT_URL, chat_id=chat_id)
        res = self._get(url)
        if res.is_success():
            return res.data

    def update_chat(self, chat_id, mq_topic=None, title=None, tag=None, ext=None):
        data = {}
        for k, v in {'mq_topic': mq_topic, 'title': title, 'tag': tag, 'ext': ext}.items():
            if v is not None:
                data[k] = v

        url = self._build_url(self.config.CHAT_URL, chat_id=chat_id)
        res = self._post(url, data)
        if res.is_success():
            return res.data['ok']

    def delete_chat(self, chat_id):
        url = self._build_url(self.config.CHAT_URL, chat_id=chat_id)
        res = self._delete(url)
        if res.is_success():
            return res.data['ok']

    def get_chat_members(self, chat_id):
        url = self._build_url(self.config.CHAT_MEMBERS_URL, chat_id=chat_id)
        res = self._get(url)
        if res.is_success():
            return res.data

    def add_chat_members(self, chat_id, users=()):
        data = {'users': users}

        url = self._build_url(self.config.CHAT_MEMBERS_URL, chat_id=chat_id)
        res = self._post(url, data)
        if res.is_success():
            return res.data['ok']

    def delete_chat_members(self, chat_id, users=()):
        data = {'users': users}
        url = self._build_url(self.config.CHAT_MEMBERS_URL, chat_id=chat_id)
        res = self._delete(url, data)
        if res.is_success():
            return res.data['ok']

    def replace_chat_members(self, chat_id, users=()):
        data = {'users': users}
        url = self._build_url(self.config.CHAT_MEMBERS_URL, chat_id=chat_id)
        res = self._put(url, data)
        if res.is_success():
            return res.data['ok']

    def send_chat_msg(self, chat_id, user, msg, domain='', perm_check=False):
        data = {
            'kind': 'chat',
            'chat_id': chat_id,
            'user': user,
            'domain': domain,
            'msg': msg,
            'perm_check': perm_check
        }
        url = self._build_url(self.config.SEND_MSG_URL)
        res = self._post(url, data)
        if res.is_success():
            ok = res.data['ok']
            if ok:
                return res.data['id'], res.data['ts']
            raise RequestFailedError(res.data['error'])
        raise RequestError(res.resp)

    def send_chat_notify_msg(self, chat_id, user, msg, domain='', perm_check=False):
        data = {
            'kind': 'chat_notify',
            'chat_id': chat_id,
            'user': user,
            'domain': domain,
            'msg': msg,
            'perm_check': perm_check
        }
        url = self._build_url(self.config.SEND_MSG_URL)
        res = self._post(url, data)
        if res.is_success():
            ok = res.data['ok']
            if ok:
                return True
            raise RequestFailedError(res.data['error'])
        raise RequestError(res.resp)
