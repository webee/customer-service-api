from urllib import parse
import threading
import requests
import logging
from datetime import datetime, timedelta
from .constant import MethodType, ErrorCode, PARAM_HEADER_MAP
from .errors import MethodTypeNotSupportedError, RequestError, RequestFailedError, RequestTokenError

logger = logging.getLogger(__name__)


class XChatClient(object):
    def __init__(self, appid, appkey, urls):
        self.appid = appid
        self.appkey = appkey
        self.urls = urls

        self._token = None
        self._token_exp = None
        self._lock = threading.RLock(blocking=False)

    def _is_current_token_valid(self):
        return self._token and self._token_exp > datetime.utcnow() + timedelta(minutes=10)

    @property
    def token(self):
        if not self._is_current_token_valid():
            with self._lock as locked:
                if locked and not self._is_current_token_valid():
                    try:
                        res = self._get_token()
                        self._token, self._token_exp = res['token'], res['exp']
                        logger.info('new token: %s, %s', self._token, self._token_exp)
                    except Exception as e:
                        raise RequestTokenError(e)
        return self._token

    def _get_url(self, type):
        url = self.urls.get(type)
        if not url:
            raise MethodTypeNotSupportedError(type)
        return url

    def build_url(self, type, path_vars=None, auth=False, is_auth=False, **kwargs):
        url = self._get_url(type)
        if path_vars is not None:
            url = url.format(**path_vars)

        scheme, netloc, path, params, query, fragment = parse.urlparse(url)

        qs = parse.parse_qs(query)
        if auth:
            qs.update(self._get_auth_qs(is_auth))
        for k, v in kwargs.items():
            if v is not None:
                qs[k] = v
        query = parse.urlencode(qs)

        return parse.urlunparse((scheme, netloc, path, params, query, fragment))

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
        if 200 <= resp.status_code < 300:
            data = resp.json()
            if not data.get('ret'):
                raise RequestFailedError(data.get('error_code', ErrorCode.REQUEST_FAILED), data.get('error_msg'))
            return data.get('data')
        raise RequestError(resp)

    def _get(self, url, **kwargs):
        return self._request('get', url, **kwargs)

    def _post(self, url, data=None, **kwargs):
        return self._request('post', url, data, **kwargs)

    def _get_token(self):
        url = self.build_url(MethodType.GET_TOKEN, auth=True, is_auth=True)
        return self._get(url)

    def get_ext_data(self, domain, type, biz_id, id=None):
        url = self.build_url(MethodType.GET_EXT_DATA, domain=domain, type=type, biz_id=biz_id, id=id)
        return self._get(url)

    def send_channel_msg(self, channel, uid, staff, type, content, project_info=None):
        url = self.build_url(MethodType.SEND_CHANNEL_MSG)
        data = {
            "channel": channel,
            "uid": uid,
            "staff_uid": staff,
            "type": type,
            "content": content,
        }
        data.update({('project_' + k): v for k, v in (project_info or {}).items()})
        self._post(url, data)
