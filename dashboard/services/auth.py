# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import logging
import json

import requests

from dashboard.libs.exceptions import HTTPUnauthorized
from dashboard import constants


logger = logging.getLogger(__name__)


class AuthLoginException(HTTPUnauthorized):
    """Subclass to HTTPUnauthorized class so that app handles this exception as-if it is HTTPUnauthorized"""
    pass


class AuthService():
    """AuthService (wrapper) to perform authentication services with the Auth Service endpoint (bouncer)

    Borg Singleton pattern
    """
    __state = {}

    @classmethod
    def set_env(cls, env):
        cls.env = env

    def _get_base_url(self):
        return constants.AUTH_SERVICE_URL_MAP.get(self.__class__.env)  # based on env settings

    def __init__(self):
        self.__dict__ = self.__state

        if 'url' not in self.__dict__:
            # init instance
            self.url = self._get_base_url()

    def _send_requests(self, url, method='get', params=None, payload=None):
        try:
            url = '/'.join([url, self.url])  # concatenate URL
            resp = requests.request(method, url, params=params, data=json.loads(payload))

            if resp.status_code >= 400:  # error occured
                raise Exception

            return resp.json() or resp.text  # return json body of response

        except:
            raise AuthLoginException()

    def login(self, payload, provider=constants.AUTH_BASIC):
        """Login method to authenticate against AuthService, returning token if successful"""

        # supported login methods
        supported_login_methods = [constants.AUTH_BASIC]

        url_map = {
            constants.AUTH_BASIC: 'auth/login/basic',
            constants.AUTH_FACEBOOK: 'auth/login/facebook'
        }

        if provider not in supported_login_methods:
            err_msg = '{} login is currently not supported.'.format(provider)
            logger.exception(err_msg)
            raise Exception(err_msg)

        # get json response from AuthService
        json_resp = self._send_requests(url_map[provider], method='post', payload=payload)
        token = json_resp.get('token')
        if not token:
            err_msg = 'token not found in response'
            logger.exception(err_msg)
            raise Exception(err_msg)

        return token