import asyncio
import logging
from asyncio import AbstractEventLoop
from typing import Union, AsyncContextManager, Optional

import aiohttp
from aiohttp import ClientTimeout
from aiohttp.client import ClientSession
from aiohttp.hdrs import METH_GET, METH_POST
from aiohttp_retry import RetryOptionsBase, RetryClient
from asyncio_throttle import Throttler

from aioetherscan.exceptions import (
    EtherscanClientContentTypeError,
    EtherscanClientError,
    EtherscanClientApiError,
    EtherscanClientProxyError,
)
from aioetherscan.url_builder import UrlBuilder


class Network:
    def __init__(
        self,
        url_builder: UrlBuilder,
        loop: Optional[AbstractEventLoop],
        timeout: Optional[ClientTimeout],
        proxy: Optional[str],
        throttler: Optional[AsyncContextManager],
        retry_options: Optional[RetryOptionsBase],
    ) -> None:
        self._url_builder = url_builder

        self._loop = loop or asyncio.get_running_loop()
        self._timeout = timeout

        self._proxy = proxy

        # Defaulting to free API key rate limit
        self._throttler = throttler or Throttler(rate_limit=5, period=1.0)

        self._retry_client = None
        self._retry_options = retry_options

        self._logger = logging.getLogger(__name__)

    async def close(self):
        if self._retry_client is not None:
            await self._retry_client.close()

    async def get(self, params: dict = None) -> Union[dict, list, str]:
        return await self._request(METH_GET, params=self._url_builder.filter_and_sign(params))

    async def post(self, data: dict = None) -> Union[dict, list, str]:
        return await self._request(METH_POST, data=self._url_builder.filter_and_sign(data))

    def _get_retry_client(self) -> RetryClient:
        return RetryClient(client_session=self._get_session(), retry_options=self._retry_options)

    def _get_session(self) -> ClientSession:
        if self._timeout is not None:
            return ClientSession(loop=self._loop, timeout=self._timeout)
        return ClientSession(loop=self._loop)

    async def _request(
        self, method: str, data: dict = None, params: dict = None
    ) -> Union[dict, list, str]:
        if self._retry_client is None:
            self._retry_client = self._get_retry_client()
        session_method = getattr(self._retry_client, method.lower())
        async with self._throttler:
            async with session_method(
                self._url_builder.API_URL, params=params, data=data, proxy=self._proxy
            ) as response:
                self._logger.debug(
                    '[%s] %r %r %s', method, str(response.url), data, response.status
                )
                return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Union[dict, list, str]:
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
    def _raise_if_error(response_json: dict):
        if 'status' in response_json and response_json['status'] != '1':
            message, result = response_json.get('message'), response_json.get('result')
            raise EtherscanClientApiError(message, result)

        if 'error' in response_json:
            err = response_json['error']
            code, message = err.get('code'), err.get('message')
            raise EtherscanClientProxyError(code, message)
