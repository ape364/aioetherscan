import asyncio
import logging
from asyncio import AbstractEventLoop
from enum import Enum
from typing import Union, Dict, List, AsyncContextManager
from urllib.parse import urlunsplit

import aiohttp
from aiohttp import ClientTimeout
from aiohttp.client import DEFAULT_TIMEOUT
from asyncio_throttle import Throttler

from aioetherscan.exceptions import EtherscanClientContentTypeError, EtherscanClientError, EtherscanClientApiError, \
    EtherscanClientProxyError


class HttpMethod(Enum):
    GET = 'get'
    POST = 'post'


class Network:
    _API_KINDS = {
        'eth': 'etherscan.io',
        'bsc': 'bscscan.com',
        'avax': 'snowtrace.io',
        'polygon': 'polygonscan.com',
        'optimism': 'etherscan.io',
        'arbitrum': 'arbiscan.io',
        'fantom': 'ftmscan.com',
    }
    BASE_URL: str = None

    def __init__(self, api_key: str, api_kind: str, network: str,
                 loop: AbstractEventLoop = None, timeout: ClientTimeout = None,
                 proxy: str = None, throttler: AsyncContextManager = None) -> None:
        self._API_KEY = api_key
        self._set_network(api_kind, network)

        self._loop = loop or asyncio.get_event_loop()
        self._timeout = timeout

        self._session = None

        self._proxy = proxy

        # Defaulting to free API key rate limit
        self._throttler = throttler or Throttler(rate_limit=5, period=1.0)

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
        async with self._throttler:
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
        try:
            base_netloc = self._API_KINDS[api_kind.lower().strip()]
        except KeyError:
            raise ValueError(f'Incorrect api_kind {api_kind!r}, supported only: {", ".join(self._API_KINDS)}')
        else:
            self._API_KIND = api_kind.lower().strip()
            self._NETWORK = network.lower().strip()

            self._API_URL = self._get_api_url(base_netloc, scheme, path)
            self.BASE_URL = self._get_base_url(base_netloc, scheme)

    def _get_api_url(self, base_netloc: str, scheme: str, path: str) -> str:
        is_main = self._NETWORK == 'main'

        if self._API_KIND == 'optimism':
            prefix = 'api-optimistic' if is_main else f'api-{self._NETWORK}-optimistic'
        else:
            prefix = 'api' if is_main else f'api-{self._NETWORK}'

        return urlunsplit((scheme, f'{prefix}.{base_netloc}', path, '', ''))

    def _get_base_url(self, base_netloc: str, scheme: str) -> str:
        if self._API_KIND == 'polygon' and self._NETWORK == 'testnet':
            network = 'mumbai'
        else:
            network = self._NETWORK

        is_main = network == 'main'

        if self._API_KIND == 'optimism':
            prefix = 'optimistic' if is_main else f'{network}-optimism'
        else:
            prefix = None if is_main else network

        return urlunsplit((scheme, base_netloc if prefix is None else f'{prefix}.{base_netloc}', '', '', ''))
