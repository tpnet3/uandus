"""
U&US API client

<http://www.uandus.net/api/v1.0/>
"""
from flask import jsonify
import requests
import logging
import datetime
from urllib.parse import urlencode

import aiohttp

from .model import *

log = logging.getLogger(__name__)


class UandusError(Exception):
    pass


class UandusClientError(UandusError):
    pass


class BaseUandusClient:
    _base_url = 'http://www.uandus.net/api/v1.0'
    _access_token_url = 'http://www.uandus.net/api/v1.0/oauth/token'

    def __init__(self, client_id, client_secret):
        self._requests = []
        self._client_id = client_id
        self._client_secret = client_secret

    def set_auth(self, access_token, refresh_token):
        self._access_token = access_token
        self._refresh_token = refresh_token
        resp = {'access_token': self._access_token,
                'refresh_token': self._refresh_token}
        return jsonify(resp)

    def _refresh_token(self):
        data = dict()
        data['grant_type'] = 'refresh_token'
        data['refresh_token'] = self._refresh_token()

        resp = requests.post(self._access_token_url, data=data)
        resp = resp.json()

        self._access_token = resp['access_token']
        self._refresh_token = resp['refresh_token']
        resp = {'access_token': self._access_token,
                'refresh_token': self._refresh_token}
        return jsonify(resp)

    def get_token(self):
        resp = {'access_token': self._access_token,
                'refresh_token': self._refresh_token}
        return jsonify(resp)

    def _get(self, path, callback=None, params=None, model_class=None):
        if params:
            path += '?' + urlencode(params)
        return self._request('GET',
                             path=path,
                             callback=callback,
                             model_class=model_class)

    def _post(self, path, callback=None, params=None, model_class=None):
        params = params or {}
        body = urlencode(params)
        return self._request('POST',
                             path=path,
                             callback=callback,
                             body=body,
                             model_class=model_class)

    def _request(self, method, path, callback=None, body=None,
                 model_class=None):
        now = datetime.datetime.utcnow()
        period_start = now - datetime.timedelta(minutes=10)
        self._requests = [dt for dt in self._requests if dt >= period_start]
        self._requests.append(now)
        log.debug('%d requests in last %d seconds',
                  len(self._requests),
                  (now - self._requests[0]).seconds)
        self._requests.append(datetime.datetime.utcnow())
        client_class = aiohttp if callback else requests
        log.debug('%s > %s %s %r', client_class.__name__, method, path, body)

        token = self._access_token
        headers = {"Authorization": "Bearer " + token}
        if method == 'GET':
            resp = requests.get(self._base_url+path, headers=headers)
        elif method == 'POST':
            resp = requests.post(self._base_url+path, headers=headers, json=body)
        else:
            resp = requests.get(self._base_url + path, headers=headers)

        if callback:
            return callback(self._process_response(resp, model_class))
        else:
            return self._process_response(resp, model_class)

    def _process_response(self, resp, model_class=None):
        model_class = model_class or Model
        log.debug('< %s %s', resp.status_code, "something")
        try:
            data = model_class(resp.json())
            # data = resp.json()
        except (ValueError, UnicodeError) as e:
            raise UandusError(
                'could not decode response json',
                resp.status_code) from e

        return data


### Public REST API methods ###
class UandusClient(BaseUandusClient):

    ##### USER ###############
    def user_me(self, callback=None):
        return self._get('/user/me', callback=callback, model_class=User)

