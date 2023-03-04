import asyncio
import json
import logging
from unittest.mock import patch, AsyncMock

import aiohttp
import pytest
from aiohttp import ClientTimeout
from aiohttp_retry import ExponentialRetry
from asyncio_throttle import Throttler
from asynctest import CoroutineMock, MagicMock
from asynctest import patch

from aioetherscan.exceptions import EtherscanClientContentTypeError, EtherscanClientError, EtherscanClientApiError, \
    EtherscanClientProxyError
from aioetherscan.network import Network, HttpMethod


class SessionMock(CoroutineMock):
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


def apikey():
    return 'testapikey'


@pytest.fixture()
async def nw():
    nw = Network(apikey(), 'eth', 'main', get_loop(), None, None, None, None)
    yield nw
    await nw.close()


def test_init():
    myloop = get_loop()
    proxy = 'qwe'
    timeout = ClientTimeout(5)
    throttler = Throttler(1)
    retry_options = ExponentialRetry()
    n = Network(apikey(), 'eth', 'main', myloop, timeout, proxy, throttler, retry_options)

    assert n._API_KEY == apikey()
    assert n._loop == myloop
    assert n._timeout is timeout
    assert n._proxy is proxy
    assert n._throttler is throttler

    assert n._retry_options is retry_options
    assert n._retry_client is None

    assert isinstance(n._logger, logging.Logger)


def test_sign(nw):
    assert nw._sign({}) == {'apikey': nw._API_KEY}
    assert nw._sign({'smth': 'smth'}) == {'smth': 'smth', 'apikey': nw._API_KEY}


def test_filter_params(nw):
    assert nw._filter_params({}) == {}
    assert nw._filter_params({1: 2, 3: None}) == {1: 2}
    assert nw._filter_params({1: 2, 3: 0}) == {1: 2, 3: 0}
    assert nw._filter_params({1: 2, 3: False}) == {1: 2, 3: False}


@pytest.mark.asyncio
async def test_get(nw):
    with patch('aioetherscan.network.Network._request', new=CoroutineMock()) as mock:
        await nw.get()
        mock.assert_called_once_with(HttpMethod.GET, params={'apikey': nw._API_KEY})


@pytest.mark.asyncio
async def test_post(nw):
    with patch('aioetherscan.network.Network._request', new=CoroutineMock()) as mock:
        await nw.post()
        mock.assert_called_once_with(HttpMethod.POST, data={'apikey': nw._API_KEY})

    with patch('aioetherscan.network.Network._request', new=CoroutineMock()) as mock:
        await nw.post({'some': 'data'})
        mock.assert_called_once_with(HttpMethod.POST, data={'apikey': nw._API_KEY, 'some': 'data'})

    with patch('aioetherscan.network.Network._request', new=CoroutineMock()) as mock:
        await nw.post({'some': 'data', 'null': None})
        mock.assert_called_once_with(HttpMethod.POST, data={'apikey': nw._API_KEY, 'some': 'data'})


@pytest.mark.asyncio
async def test_request(nw):
    class MagicMockContext(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            type(self).__aenter__ = CoroutineMock(return_value=MagicMock())
            type(self).__aexit__ = CoroutineMock(return_value=MagicMock())

    nw._retry_client = AsyncMock()

    throttler_mock = AsyncMock()
    nw._throttler = AsyncMock()
    nw._throttler.__aenter__ = throttler_mock

    get_mock = MagicMockContext()
    nw._retry_client.get = get_mock
    with patch('aioetherscan.network.Network._handle_response', new=CoroutineMock()) as h:
        await nw._request(HttpMethod.GET)
        throttler_mock.assert_awaited_once()
        get_mock.assert_called_once_with('https://api.etherscan.io/api', params=None, data=None, proxy=None)
        h.assert_called_once()

    post_mock = MagicMockContext()
    nw._retry_client.post = post_mock
    with patch('aioetherscan.network.Network._handle_response', new=CoroutineMock()) as h:
        await nw._request(HttpMethod.POST)
        throttler_mock.assert_awaited()
        post_mock.assert_called_once_with('https://api.etherscan.io/api', params=None, data=None, proxy=None)
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

        async def text(self):
            return 'some text'

        async def json(self):
            if self.raise_exc:
                raise self.raise_exc
            return json.loads(self.data)

    with pytest.raises(EtherscanClientContentTypeError) as e:
        await nw._handle_response(MockResponse('qweasd', aiohttp.ContentTypeError('info', 'hist')))
    assert e.value.status == 200
    assert e.value.content == 'some text'

    with pytest.raises(EtherscanClientError, match='some exc'):
        await nw._handle_response(MockResponse('qweasd', Exception('some exc')))

    with pytest.raises(EtherscanClientApiError) as e:
        await nw._handle_response(MockResponse('{"status": "0", "message": "NOTOK", "result": "res"}'))
    assert e.value.message == 'NOTOK'
    assert e.value.result == 'res'

    with pytest.raises(EtherscanClientProxyError) as e:
        await nw._handle_response(MockResponse('{"error": {"code": "100", "message": "msg"}}'))
    assert e.value.code == '100'
    assert e.value.message == 'msg'

    assert await nw._handle_response(MockResponse('{"result": "someresult"}')) == 'someresult'


@pytest.mark.asyncio
async def test_close_session(nw: Network):
    with patch('aiohttp.ClientSession.close', new_callable=CoroutineMock) as m:
        await nw.close()
        m: CoroutineMock
        m.assert_not_called()

        nw._retry_client = MagicMock()
        nw._retry_client.close = CoroutineMock()
        await nw.close()
        nw._retry_client.close.assert_called_once()


@pytest.mark.parametrize(
    "api_kind,network_name,expected",
    [
        ('eth', 'main', 'https://api.etherscan.io/api'),
        ('eth', 'ropsten', 'https://api-ropsten.etherscan.io/api'),
        ('eth', 'kovan', 'https://api-kovan.etherscan.io/api'),
        ('eth', 'rinkeby', 'https://api-rinkeby.etherscan.io/api'),
        ('eth', 'goerli', 'https://api-goerli.etherscan.io/api'),
        ('eth', 'sepolia', 'https://api-sepolia.etherscan.io/api'),
        ('bsc', 'main', 'https://api.bscscan.com/api'),
        ('bsc', 'testnet', 'https://api-testnet.bscscan.com/api'),
        ('avax', 'main', 'https://api.snowtrace.io/api'),
        ('avax', 'testnet', 'https://api-testnet.snowtrace.io/api'),
        ('polygon', 'main', 'https://api.polygonscan.com/api'),
        ('polygon', 'testnet', 'https://api-testnet.polygonscan.com/api'),
        ('optimism', 'main', 'https://api-optimistic.etherscan.io/api'),
        ('optimism', 'goerli', 'https://api-goerli-optimistic.etherscan.io/api'),
        ('arbitrum', 'main', 'https://api.arbiscan.io/api'),
        ('arbitrum', 'nova', 'https://api-nova.arbiscan.io/api'),
        ('arbitrum', 'goerli', 'https://api-goerli.arbiscan.io/api'),
        ('fantom', 'main', 'https://api.ftmscan.com/api'),
        ('fantom', 'testnet', 'https://api-testnet.ftmscan.com/api'),
    ]
)
def test_test_network(api_kind, network_name, expected):
    nw = Network(apikey(), api_kind, network_name, None, None, None, None, None)
    assert nw._API_URL == expected


def test_invalid_api_kind():
    with pytest.raises(ValueError) as excinfo:
        Network(apikey(), 'wrong', 'main', None, None, None, None, None)
    assert 'Incorrect api_kind' in str(excinfo.value)
