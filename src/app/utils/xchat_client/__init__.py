from urllib import parse
import threading
import requests
import jwt
import logging
from datetime import datetime, timedelta
from pytoolbox.util import pmc_config
from .config import Config
from . import constant

logger = logging.getLogger(__name__)


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

    def __init__(self, ns='', key='<jwt key>', env_config=None):
        self.ns = ns
        self.key = key
        self.config = Config()
        self._token = None
        self._token_exp = None
        self._lock = threading.RLock()

        if env_config is not None:
            self.init_config(env_config)

    def init_config(self, ns, key, env_config):
        self.ns = ns
        self.key = key
        pmc_config.merge_config(self.config, env_config)

    def _new_token(self):
        exp = datetime.utcnow() + timedelta(days=30)
        payload = dict(
            ns=self.ns,
            is_admin=True,
            exp=exp
        )

        return jwt.encode(payload, self.key).decode('utf-8'), exp

    def _is_current_token_valid(self):
        return self._token and self._token_exp > datetime.utcnow() + timedelta(minutes=30)

    @property
    def token(self):
        if not self._is_current_token_valid():
            with self._lock:
                if not self._is_current_token_valid():
                    self._token, self._token_exp = self._new_token()
                    logger.info('new token: %s, %s', self._token, self._token_exp)
        return self._token

    def _build_url(self, path, path_vars=None, **kwargs):
        path = path.lstrip('/')
        path = path.format(**(path_vars or {}))

        scheme, netloc, root_path, params, root_query, fragment = parse.urlparse(self.config.ROOT_URL)
        path = parse.urljoin(root_path, path)

        qs = parse.parse_qs(root_query)
        for k, v in kwargs.items():
            if v is not None:
                qs[k] = v
        query = parse.urlencode(qs)

        return parse.urlunparse((scheme, netloc, path, params, query, fragment))

    def _request(self, method, url, data=None, **kwargs):
        logger.debug('request: %s, %s, %s', method, url, data)
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

    def new_chat(self, chat_type, users=(), app_id=None, biz_id=None, start_msg_id=None, title=None, tag=None, ext=None):
        data = {'type': chat_type, 'users': users}
        for k, v in dict(app_id=app_id, biz_id=biz_id, start_msg_id=start_msg_id, title=title, tag=tag, ext=ext).items():
            if v is not None:
                data[k] = v

        url = self._build_url(self.config.CHATS_PATH)
        res = self._post(url, data)
        if res.is_success():
            return res.data['id']
        raise RequestError(res.resp)

    def get_chat(self, chat_id):
        url = self._build_url(self.config.CHAT_PATH, dict(chat_id=chat_id))
        res = self._get(url)
        if res.is_success():
            return res.data

    def update_chat(self, chat_id, mq_topic=None, title=None, tag=None, ext=None):
        data = {}
        for k, v in {'mq_topic': mq_topic, 'title': title, 'tag': tag, 'ext': ext}.items():
            if v is not None:
                data[k] = v

        url = self._build_url(self.config.CHAT_PATH, dict(chat_id=chat_id))
        res = self._post(url, data)
        if res.is_success():
            return res.data['ok']

    def delete_chat(self, chat_id):
        url = self._build_url(self.config.CHAT_PATH, dict(chat_id=chat_id))
        res = self._delete(url)
        if res.is_success():
            return res.data['ok']

    def get_chat_members(self, chat_id):
        url = self._build_url(self.config.CHAT_MEMBERS_PATH, dict(chat_id=chat_id))
        res = self._get(url)
        if res.is_success():
            return res.data

    def add_chat_members(self, chat_id, users=()):
        data = {'users': users}

        url = self._build_url(self.config.CHAT_MEMBERS_PATH, dict(chat_id=chat_id))
        res = self._post(url, data)
        if res.is_success():
            return res.data['ok']

    def delete_chat_members(self, chat_id, users=()):
        data = {'users': users}
        url = self._build_url(self.config.CHAT_MEMBERS_PATH, dict(chat_id=chat_id))
        res = self._delete(url, data)
        if res.is_success():
            return res.data['ok']

    def replace_chat_members(self, chat_id, users=()):
        data = {'users': users}
        url = self._build_url(self.config.CHAT_MEMBERS_PATH, dict(chat_id=chat_id))
        res = self._put(url, data)
        if res.is_success():
            return res.data['ok']

    def insert_chat_msgs(self, chat_id, msgs=()):
        """ 往会话前面插入消息
        :param chat_id: 会话id
        :param msgs: [{uid, msg, ts, domain}, ...]
        :return: 是否成功，成功插入条数
        """
        data = {'msgs': msgs}
        url = self._build_url(self.config.INSERT_CHAT_MESSAGES_PATH, dict(chat_id=chat_id))
        res = self._post(url, data)
        if res.is_success():
            return res.data['ok'], res.data.get('n', 0)
        raise RequestError(res.resp)

    def send_msg(self, kind, chat_id, user, msg, domain='', perm_check=False, msg_notify=False):
        data = {
            'kind': kind,
            'chat_id': chat_id,
            'user': user,
            'domain': domain,
            'msg': msg,
            'perm_check': perm_check,
            'msg_notify': msg_notify
        }
        url = self._build_url(self.config.SEND_MSG_PATH)
        res = self._post(url, data)
        if res.is_success():
            ok = res.data['ok']
            if ok:
                return res.data
            raise RequestFailedError(res.data['error'])
        raise RequestError(res.resp)

    def send_chat_msg(self, chat_id, user, msg, domain='', perm_check=False, msg_notify=False):
        data = self.send_msg('chat', chat_id, user, msg, domain, perm_check, msg_notify)
        return data['id'], data['ts']

    def send_chat_notify_msg(self, chat_id, user, msg, domain='', perm_check=False, msg_notify=False):
        return self.send_msg('chat_notify', chat_id, user, msg, domain, perm_check, msg_notify)

    def fetch_chat_msgs(self, chat_id, lid=None, rid=None, limit=None, desc=None):
        url = self._build_url(self.config.FETCH_CHAT_MSGS_PATH, dict(chat_id=chat_id),
                              lid=lid, rid=rid, limit=limit, desc=desc)
        res = self._get(url)
        if res.is_success():
            return res.data
        raise RequestError(res.resp)
