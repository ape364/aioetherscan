import asyncio
import logging
from asyncio import AbstractEventLoop
from enum import Enum
from typing import Union, Dict, List
from urllib.parse import urlunsplit

import aiohttp
from aiohttp import ClientTimeout
from aiohttp.client import DEFAULT_TIMEOUT

from aioetherscan.exceptions import EtherscanClientContentTypeError, EtherscanClientError, EtherscanClientApiError, \
    EtherscanClientProxyError


class HttpMethod(Enum):
    GET = 'get'
    POST = 'post'


class Network:
    _API_KINDS = {
        'eth': 'etherscan.io',
        'bsc': 'bscscan.com',
        'avax': 'snowtrace.io'
    }
    BASE_URL: str = None

    def __init__(self, api_key: str, api_kind: str, network: str,
                 loop: AbstractEventLoop = None, timeout: ClientTimeout = None, proxy: str = None) -> None:
        self._API_KEY = api_key
        self._set_network(api_kind, network)

        self._loop = loop or asyncio.get_event_loop()
        self._timeout = timeout

        self._session = None

        self._proxy = proxy

        self._logger = logging.getLogger(__name__)

    async def close(self):
        if self._session is not None:
            await self._session.close()

    async def get(self, params: Dict = None) -> Union[Dict, List, str]:
        return await self._request(HttpMethod.GET, params=self._filter_and_sign(params))

    async def post(self, data: Dict = None) -> Union[Dict, List, str]:
        return await self._request(HttpMethod.POST, data=self._filter_and_sign(data))

    async def _request(self, method: HttpMethod, data: Dict = None, params: Dict = None) -> Union[Dict, List, str]:
        if self._timeout is None:
            self._timeout = DEFAULT_TIMEOUT
        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self._loop, timeout=self._timeout)
        session_method = getattr(self._session, method.value)
        async with session_method(self._API_URL, params=params, data=data, proxy=self._proxy) as response:
            self._logger.debug('[%s] %r %r %s', method.name, str(response.url), data, response.status)
            return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Union[Dict, list, str]:
        try:
            response_json = await response.json()
        except aiohttp.ContentTypeError:
            raise EtherscanClientContentTypeError(response.status, await response.text())
        except Exception as e:
            raise EtherscanClientError(e)
        else:
            self._logger.debug('Response: %r', response_json)
            self._raise_if_error(response_json)
            return response_json['result']

    @staticmethod
    def _raise_if_error(response_json: Dict):
        if 'status' in response_json and response_json['status'] != '1':
            message, result = response_json.get('message'), response_json.get('result')
            raise EtherscanClientApiError(message, result)

        if 'error' in response_json:
            err = response_json['error']
            code, message = err.get('code'), err.get('message')
            raise EtherscanClientProxyError(code, message)

    def _filter_and_sign(self, params: Dict):
        return self._sign(
            self._filter_params(params or {})
        )

    def _sign(self, params: Dict) -> Dict:
        if not params:
            params = {}
        params['apikey'] = self._API_KEY
        return params

    @staticmethod
    def _filter_params(params: Dict) -> Dict:
        return {k: v for k, v in params.items() if v is not None}

    def _set_network(self, api_kind: str, network: str, scheme: str = 'https', path: str = 'api') -> None:
        # https://docs.etherscan.io/getting-started/endpoint-urls
        try:
            base_netloc = self._API_KINDS[api_kind.lower().strip()]
        except KeyError:
            raise ValueError(f'Incorrect api_kind {api_kind!r}, supported only: {", ".join(self._API_KINDS)}')

        network_name = network.lower().strip()
        prefix = 'api' if network_name == 'main' else f'api-{network_name}'
        self.BASE_URL = urlunsplit((scheme, base_netloc, '', '', ''))
        self._API_URL = urlunsplit((scheme, f'{prefix}.{base_netloc}', path, '', ''))
