import asyncio
import json
import logging
from unittest.mock import patch, AsyncMock, MagicMock, Mock, call

import aiohttp
import aiohttp_retry
import pytest
import pytest_asyncio
from aiohttp import ClientTimeout
from aiohttp.hdrs import METH_GET, METH_POST
from aiohttp_retry import ExponentialRetry
from asyncio_throttle import Throttler

from aioetherscan.exceptions import (
    EtherscanClientContentTypeError,
    EtherscanClientError,
    EtherscanClientApiError,
    EtherscanClientProxyError,
    EtherscanClientApiRateLimitError,
)
from aioetherscan.network import Network, retry_limit_attempt
from aioetherscan.url_builder import UrlBuilder


class SessionMock(AsyncMock):
    # noinspection PyUnusedLocal
    @pytest.mark.asyncio
    async def get(self, url, params, data):
        return AsyncCtxMgrMock()


class AsyncCtxMgrMock(MagicMock):
    @pytest.mark.asyncio
    async def __aenter__(self):
        return self.aenter

    @pytest.mark.asyncio
    async def __aexit__(self, *args):
        pass


def get_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture
async def ub():
    ub = UrlBuilder(['test_api_key'], 'eth', 'main')
    yield ub


@pytest_asyncio.fixture
async def nw(ub):
    nw = Network(ub, get_loop(), None, None, None, None)
    yield nw
    await nw.close()


def test_init(ub):
    myloop = get_loop()
    proxy = 'qwe'
    timeout = ClientTimeout(5)
    throttler = Throttler(1)
    retry_options = ExponentialRetry()
    n = Network(ub, myloop, timeout, proxy, throttler, retry_options)

    assert n._url_builder is ub
    assert n._loop == myloop
    assert n._timeout is timeout
    assert n._proxy is proxy
    assert n._throttler is throttler

    assert n._retry_options is retry_options
    assert n._retry_client is None

    assert isinstance(n._logger, logging.Logger)


def test_no_loop(ub):
    with pytest.raises(RuntimeError) as e:
        Network(ub, None, None, None, None, None)
    assert str(e.value) == 'no running event loop'


@pytest.mark.asyncio
async def test_get(nw):
    with patch('aioetherscan.network.Network._request', new=AsyncMock()) as mock:
        await nw.get()
        mock.assert_called_once_with(METH_GET, params={'apikey': nw._url_builder._api_key})


@pytest.mark.asyncio
async def test_post(nw):
    with patch('aioetherscan.network.Network._request', new=AsyncMock()) as mock:
        await nw.post()
        mock.assert_called_once_with(METH_POST, data={'apikey': nw._url_builder._api_key})

    with patch('aioetherscan.network.Network._request', new=AsyncMock()) as mock:
        await nw.post({'some': 'data'})
        mock.assert_called_once_with(
            METH_POST, data={'apikey': nw._url_builder._api_key, 'some': 'data'}
        )

    with patch('aioetherscan.network.Network._request', new=AsyncMock()) as mock:
        await nw.post({'some': 'data', 'null': None})
        mock.assert_called_once_with(
            METH_POST, data={'apikey': nw._url_builder._api_key, 'some': 'data'}
        )


@pytest.mark.asyncio
async def test_request(nw):
    class MagicMockContext(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            type(self).__aenter__ = AsyncMock(return_value=MagicMock())
            type(self).__aexit__ = AsyncMock(return_value=MagicMock())

    throttler_mock = AsyncMock()
    nw._throttler = AsyncMock()
    nw._throttler.__aenter__ = throttler_mock

    retry_client_mock = Mock()
    retry_client_mock.get = MagicMockContext()
    retry_client_mock.close = AsyncMock()
    nw._get_retry_client = Mock(return_value=retry_client_mock)

    with patch('aioetherscan.network.Network._handle_response', new=AsyncMock()) as h:
        await nw._request(METH_GET)
        throttler_mock.assert_awaited_once()
        retry_client_mock.get.assert_called_once_with(
            'https://api.etherscan.io/api', params=None, data=None, proxy=None
        )
        h.assert_called_once()

    post_mock = MagicMockContext()
    nw._retry_client.post = post_mock
    with patch('aioetherscan.network.Network._handle_response', new=AsyncMock()) as h:
        await nw._request(METH_POST)
        nw._get_retry_client.assert_called_once()
        throttler_mock.assert_awaited()
        post_mock.assert_called_once_with(
            'https://api.etherscan.io/api', params=None, data=None, proxy=None
        )
        h.assert_called_once()

    assert throttler_mock.call_count == 2


# noinspection PyTypeChecker
@pytest.mark.asyncio
async def test_handle_response(nw):
    class MockResponse:
        def __init__(self, data, raise_exc=None):
            self.data = data
            self.raise_exc = raise_exc

        @property
        def status(self):
            return 200

        # noinspection PyMethodMayBeStatic
        async def text(self):
            return 'some text'

        async def json(self):
            if self.raise_exc:
                raise self.raise_exc
            return json.loads(self.data)

    with pytest.raises(EtherscanClientContentTypeError) as e:
        await nw._handle_response(MockResponse('some', aiohttp.ContentTypeError('info', 'hist')))
    assert e.value.status == 200
    assert e.value.content == 'some text'

    with pytest.raises(EtherscanClientError, match='some exc'):
        await nw._handle_response(MockResponse('some', Exception('some exception')))

    with pytest.raises(EtherscanClientApiError) as e:
        await nw._handle_response(
            MockResponse('{"status": "0", "message": "NOTOK", "result": "res"}')
        )
    assert e.value.message == 'NOTOK'
    assert e.value.result == 'res'

    with pytest.raises(EtherscanClientProxyError) as e:
        await nw._handle_response(MockResponse('{"error": {"code": "100", "message": "msg"}}'))
    assert e.value.code == '100'
    assert e.value.message == 'msg'

    assert await nw._handle_response(MockResponse('{"result": "some_result"}')) == 'some_result'


@pytest.mark.asyncio
async def test_close_session(nw):
    with patch('aiohttp.ClientSession.close', new_callable=AsyncMock) as m:
        await nw.close()
        m: AsyncMock
        m.assert_not_called()

        nw._retry_client = MagicMock()
        nw._retry_client.close = AsyncMock()
        await nw.close()
        nw._retry_client.close.assert_called_once()


def test_get_session_timeout_is_none(nw):
    with patch('aiohttp.ClientSession.__new__', new=Mock()) as m:
        session = nw._get_session()

        m.assert_called_once_with(
            aiohttp.ClientSession,
            loop=nw._loop,
        )

        assert session is m.return_value


def test_get_session_timeout_is_not_none(nw):
    nw._timeout = 1

    with patch('aiohttp.ClientSession.__new__', new=Mock()) as m:
        session = nw._get_session()

        m.assert_called_once_with(aiohttp.ClientSession, loop=nw._loop, timeout=nw._timeout)

        assert session is m.return_value


def test_get_retry_client(nw):
    nw._get_session = Mock()

    with patch('aiohttp_retry.RetryClient.__new__', new=Mock()) as m:
        result = nw._get_retry_client()
        m.assert_called_once_with(
            aiohttp_retry.RetryClient,
            client_session=nw._get_session.return_value,
            retry_options=nw._retry_options,
        )
        assert result is m.return_value


def test_raise_if_error_daily_limit_reached(nw):
    data = dict(
        status='0',
        message='NOTOK',
        result='Max daily rate limit reached. 110000 (100%) of 100000 day/limit',
    )
    with pytest.raises(EtherscanClientApiRateLimitError) as e:
        nw._raise_if_error(data)

    assert e.value.message == data['message']
    assert e.value.result == data['result']


class TestRetryClass:
    def __init__(self, limit: int, keys_count: int):
        self._url_builder = Mock()
        self._url_builder.keys_count = keys_count
        self._url_builder.rotate_api_key = Mock()

        self._logger = Mock()
        self._logger.warning = Mock()

        self._count = 1
        self._limit = limit

    @retry_limit_attempt
    async def some_method(self):
        self._count += 1

        if self._count > self._limit:
            raise EtherscanClientApiRateLimitError(
                'NOTOK',
                'Max daily rate limit reached. 110000 (100%) of 100000 day/limit',
            )


@pytest.mark.asyncio
async def test_retry_limit_attempt_error_limit_exceeded(nw):
    c = TestRetryClass(1, 1)

    with pytest.raises(EtherscanClientApiRateLimitError):
        await c.some_method()
    c._url_builder.rotate_api_key.assert_not_called()
    c._logger.warning.assert_called_once_with(
        'Key daily limit exceeded, attempt=1: [NOTOK] Max daily rate limit reached. 110000 (100%) of 100000 day/limit'
    )


@pytest.mark.asyncio
async def test_retry_limit_attempt_error_limit_rotate(nw):
    c = TestRetryClass(1, 2)

    with pytest.raises(EtherscanClientApiRateLimitError):
        await c.some_method()
    c._url_builder.rotate_api_key.assert_called_once()
    c._logger.warning.assert_has_calls(
        [
            call(
                'Key daily limit exceeded, attempt=1: [NOTOK] Max daily rate limit reached. 110000 (100%) of 100000 day/limit'
            ),
            call(
                'Key daily limit exceeded, attempt=2: [NOTOK] Max daily rate limit reached. 110000 (100%) of 100000 day/limit'
            ),
        ]
    )


@pytest.mark.asyncio
async def test_retry_limit_attempt_ok(nw):
    c = TestRetryClass(2, 1)

    await c.some_method()
