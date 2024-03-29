from urllib import parse
from threading import RLock
import requests
import logging
import time
from datetime import datetime, timedelta
from . import constant
from .constant import MethodType, ErrorCode, PARAM_HEADER_MAP
from .errors import MethodTypeNotSupportedError, RequestError, RequestFailedError, RequestTokenError, RequestAuthFailedError

logger = logging.getLogger(__name__)


class AppClients(object):
    def __init__(self, app=None, cache=None):
        self.app = app
        self.cache = cache

    def init_app(self, app, cache):
        self.app = app
        self.cache = cache

    def update_app_token(self, appid, token, exp):
        timeout = int(exp - (time.time() + time.timezone))
        if timeout > 0:
            self.cache.set(self._gen_key(appid), (token, exp), timeout=timeout)
        else:
            self.cache.delete(self._gen_key(appid))

    @staticmethod
    def _gen_key(appid):
        return 'app_client_' + appid

    def get_client(self, appid, appkey, urls):
        token, exp = self.cache.get(self._gen_key(appid)) or (None, None)
        return AppClient(appid, appkey, urls, token=token, exp=exp, token_update_callback=self.update_app_token)


class AppClient(object):
    constant = constant

    def __init__(self, appid, appkey, urls, token=None, exp=None, token_update_callback=None):
        self.appid = appid
        self.appkey = appkey
        self.urls = urls

        self._token_update_callback = token_update_callback
        self._token = token
        self._token_exp = datetime.utcfromtimestamp(exp) if exp is not None else None
        self._lock = RLock()

    def _is_current_token_valid(self):
        return self._token and self._token_exp > datetime.utcnow() + timedelta(minutes=10)

    @property
    def token(self):
        if not self._is_current_token_valid():
            with self._lock:
                if not self._is_current_token_valid():
                    try:
                        res = self._get_token()
                        token, exp = res['token'], res['exp']
                        self._token, self._token_exp = token, datetime.utcfromtimestamp(exp)
                        if self._token_update_callback:
                            self._token_update_callback(self.appid, token, exp)
                        logger.info('new token: %s, %s', self._token, self._token_exp)
                    except (MethodTypeNotSupportedError, ConnectionError):
                        raise
                    except Exception as e:
                        raise RequestTokenError(e)
        return self._token

    def _get_url(self, method_type):
        url = self.urls.get(method_type)
        if not url:
            raise MethodTypeNotSupportedError(method_type)
        return url

    def _build_url(self, method_type, path_vars=None, auth=False, is_auth=False, params=None):
        url = self._get_url(method_type)
        if path_vars is not None:
            url = url.format(**path_vars)

        scheme, netloc, path, path_params, query, fragment = parse.urlparse(url)

        qs = parse.parse_qs(query)
        if auth:
            qs.update(self._get_auth_qs(is_auth))
        for k, v in (params or {}).items():
            if v is not None:
                qs[k] = v
        query = parse.urlencode(qs, doseq=True)

        return parse.urlunparse((scheme, netloc, path, path_params, query, fragment))

    def _get_auth_qs(self, is_auth=False):
        if not is_auth and self._get_url(MethodType.GET_TOKEN):
            return {'appid': self.appid, 'token': self.token}
        return {'appid': self.appid, 'appkey': self.appkey}

    def _get_auth_headers(self, is_auth=False):
        return {PARAM_HEADER_MAP[k]: v for k, v in self._get_auth_qs(is_auth).items()}

    def _request(self, method, url, data=None, auth=True, is_auth=False, **kwargs):
        logger.debug('request: %s, %s, %s', method, url, data)
        headers = {}
        if auth:
            headers.update(self._get_auth_headers(is_auth))
        if 'timeout' not in kwargs:
            # 默认15秒超时
            kwargs['timeout'] = 15
        resp = requests.request(method, url, json=data, headers=headers, **kwargs)
        logger.debug('response: %s, %s, %s, %s', method, url, resp.status_code, resp.headers)
        if 200 <= resp.status_code < 300:
            data = resp.json()
            if not data.get('ret'):
                error_code = data.get('error_code', ErrorCode.REQUEST_FAILED)
                if error_code <= 3:
                    if self._token_update_callback:
                        # delete token cache
                        self._token_update_callback(self.appid, None, 0)
                    raise RequestAuthFailedError(error_code, data.get('error_msg'))
                raise RequestFailedError(error_code, data.get('error_msg'))
            return data.get('data')
        raise RequestError(resp)

    def _get(self, url, **kwargs):
        return self._request('get', url, **kwargs)

    def _post(self, url, data=None, **kwargs):
        return self._request('post', url, data, **kwargs)

    def _get_token(self):
        url = self._build_url(MethodType.GET_TOKEN, auth=True, is_auth=True)
        return self._get(url, auth=False)

    def get_ext_data(self, domain, type, biz_id, id=None):
        url = self._build_url(MethodType.GET_EXT_DATA, params=dict(domain=domain, type=type, biz_id=biz_id, id=id))
        return self._get(url)

    def send_channel_msg(self, channel, uid, staff, type, content, project_info=None):
        url = self._build_url(MethodType.SEND_CHANNEL_MSG)
        data = {
            "channel": channel,
            "uid": uid,
            "staff_uid": staff,
            "type": type,
            "content": content,
        }
        data.update({('project_' + k): v for k, v in (project_info or {}).items()})
        self._post(url, data)

    def push_msg(self, uid, title, content, project_info=None):
        url = self._build_url(MethodType.PUSH_MSG)
        data = {
            "uid": uid,
            "title": title,
            "content": content,
        }
        data.update({('project_' + k): v for k, v in (project_info or {}).items()})
        self._post(url, data)

    def build_access_function_url(self, domain, type, biz_id, owner, func, id=None, uid=None):
        return self._build_url(MethodType.ACCESS_FUNCTION, auth=True,
                               params=dict(domain=domain, type=type, biz_id=biz_id, id=id, owner=owner, uid=uid,
                                           function=func))
