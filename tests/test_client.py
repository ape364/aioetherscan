from unittest.mock import patch, AsyncMock, PropertyMock

import pytest
import pytest_asyncio

from aioetherscan import Client
from aioetherscan.modules.account import Account
from aioetherscan.modules.block import Block
from aioetherscan.modules.contract import Contract
from aioetherscan.modules.extra.links import LinkHelper
from aioetherscan.modules.extra.utils import Utils
from aioetherscan.modules.logs import Logs
from aioetherscan.modules.proxy import Proxy
from aioetherscan.modules.stats import Stats
from aioetherscan.modules.transaction import Transaction
from aioetherscan.network import Network
from aioetherscan.url_builder import UrlBuilder


@pytest_asyncio.fixture
async def client():
    c = Client('TestApiKey')
    yield c
    await c.close()


def test_api_key():
    with pytest.raises(TypeError):
        # noinspection PyArgumentList,PyUnusedLocal
        c = Client()


def test_init(client):
    assert isinstance(client._url_builder, UrlBuilder)
    assert isinstance(client._http, Network)

    assert isinstance(client.account, Account)
    assert isinstance(client.block, Block)
    assert isinstance(client.contract, Contract)
    assert isinstance(client.transaction, Transaction)
    assert isinstance(client.stats, Stats)
    assert isinstance(client.logs, Logs)
    assert isinstance(client.proxy, Proxy)

    assert isinstance(client.utils, Utils)
    assert isinstance(client.links, LinkHelper)

    assert isinstance(client.account._client, Client)
    assert isinstance(client.block._client, Client)
    assert isinstance(client.contract._client, Client)
    assert isinstance(client.transaction._client, Client)
    assert isinstance(client.stats._client, Client)
    assert isinstance(client.logs._client, Client)
    assert isinstance(client.proxy._client, Client)

    assert isinstance(client.utils._client, Client)
    assert isinstance(client.links._url_builder, UrlBuilder)


@pytest.mark.asyncio
async def test_close_session(client):
    with patch('aioetherscan.network.Network.close', new_callable=AsyncMock) as m:
        await client.close()
        m.assert_called_once_with()


def test_currency(client):
    with patch('aioetherscan.url_builder.UrlBuilder.currency', new_callable=PropertyMock) as m:
        currency = 'ETH'
        m.return_value = currency

        assert client.currency == currency
        m.assert_called_once()
