import asyncio
import logging
from enum import Enum
from typing import Union, Dict, List

import aiohttp

from aioetherscan.exceptions import EtherscanClientContentTypeError, EtherscanClientError, EtherscanClientApiError, \
    EtherscanClientProxyError


class HttpMethod(Enum):
    GET = 'get'
    POST = 'post'


class Network:
    _API_KINDS = ('eth', 'bsc')
    _ETH_NETWORKS = {
        'main': 'https://api.etherscan.io/api',
        'ropsten': 'https://api-ropsten.etherscan.io/api',  # ROPSTEN (Revival) TESTNET
        'kovan': 'https://api-kovan.etherscan.io/api',  # KOVAN (POA) TESTNET
        'rinkeby': 'https://api-rinkeby.etherscan.io/api',  # RINKEBY (CLIQUE) TESTNET
        'goerli': 'https://api-goerli.etherscan.io/api',  # GOERLI (GTH) TESTNET
        'tobalaba': 'https://api-tobalaba.etherscan.com/api'  # TOBALABA NETWORK
    }

    _BSC_NETWORKS = {
        'main': 'https://api.bscscan.com/api',
        'test': 'https://api-testnet.bscscan.com/api',
    }

    def __init__(self, api_key: str, api_kind: str, network: str, loop: asyncio.AbstractEventLoop) -> None:
        self._API_KEY = api_key
        self._set_network(api_kind, network)

        self._loop = loop or asyncio.get_event_loop()
        self._session = None

        self._logger = logging.getLogger(__name__)

    async def close(self):
        if self._session is not None:
            await self._session.close()

    async def get(self, params: Dict = None) -> Union[Dict, List, str]:
        return await self._request(HttpMethod.GET, params=self._filter_and_sign(params))

    async def post(self, data: Dict = None) -> Union[Dict, List, str]:
        return await self._request(HttpMethod.POST, data=self._filter_and_sign(data))

    async def _request(self, method: HttpMethod, data: Dict = None, params: Dict = None) -> Union[Dict, List, str]:
        if self._session is None:
            self._session = aiohttp.ClientSession(loop=self._loop)
        session_method = getattr(self._session, method.value)
        async with session_method(self._API_URL, params=params, data=data) as response:
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

    def _set_network(self, api_kind: str, network: str) -> None:
        kind = api_kind.lower().strip()

        if kind == 'eth':
            networks = self._ETH_NETWORKS
        elif kind == 'bsc':
            networks = self._BSC_NETWORKS
        else:
            raise ValueError(f'Incorrect api_kind {api_kind!r}, supported only: {", ".join(self._API_KINDS)}')

        if network not in networks:
            raise ValueError(f'Incorrect network {network!r}, supported only: {", ".join(networks.keys())}')
        self._API_URL = networks[network]
