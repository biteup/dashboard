# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import logging
import copy
import json
from string import Formatter
import requests
from dashboard import constants

logger = logging.getLogger(__name__)


class APIException(Exception):
    pass

API_MAP = {
    # This is a map of method names to their corresponding API endpoints with the backend (HTTPS)
    # method names are almost CRUD-speak (since our backend API tries to be RESTful)
    # CREATE, GET, UPDATE, DELETE (CGUD)
    'get_menus': {
        'url': 'menus',
        'method': 'get'
    },
    'get_menu': {
        'url': 'menus/{id}',
        'method': 'get'
    },
    'update_menu': {
        'url': 'menus/{id}',
        'method': 'put'
    },
    'delete_menu': {
        'url': 'menus/{id}',
        'method': 'delete'
    },
    'get_restaurants': {
        'url': 'restaurants',
        'method': 'get'
    },
    'get_tags': {
        'url': 'tags',
        'method': 'get'
    },
    'get_user': {
        'url': 'users/{id}',
        'method': 'get'
    }
}


class APIService():
    """API Service (wrapper) to communicate with backend API Service (Snakebite)"""

    @classmethod
    def set_env(cls, env):
        cls.env = env

    def _get_base_url(self):
        return constants.API_SERVICE_URL_MAP[self.__class__.env]

    def __init__(self, token):
        self.token = token
        self.base_url = self._get_base_url()

    def __getattr__(self, api_call):

        def _send_requests(self, **kwargs):
            if api_call not in API_MAP:
                raise APIException('unsupported method')

            fn = API_MAP[api_call]
            kwargs = copy.deepcopy(kwargs)

            try:
                url = '/'.join([self.base_url, fn['url']])  # concatenate URL
                params = kwargs
                params.update({'token': self.token})  # add token for verification
                url_keys = [tup[1] for tup in Formatter().parse(fn['url']) if tup[1] is not None]
                if url_keys:
                    url = url.format(**{key: kwargs.pop(key) for key in url_keys})  # pad URL with required keys (e.g., id)

                headers = {'Content-type': 'application/json'}
                resp = requests.request(fn['method'], url, headers=headers, params=params, data=json.dumps(kwargs))

                if resp.status_code >= 400:  # error occured
                    raise Exception

                return resp.json() or resp.text  # return json body of response

            except Exception as e:
                print(e.message)
                raise APIException(e.message)

        return _send_requests.__get__(self)
