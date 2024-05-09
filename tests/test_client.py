from unittest.mock import patch, AsyncMock, PropertyMock, Mock

import pytest
import pytest_asyncio

from aioetherscan import Client
from aioetherscan.modules.account import Account
from aioetherscan.modules.block import Block
from aioetherscan.modules.contract import Contract
from aioetherscan.modules.extra import ExtraModules, ContractUtils
from aioetherscan.modules.extra.generators.account_proxy import GeneratorUtils
from aioetherscan.modules.extra.link import LinkUtils
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
        Client()


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

    assert isinstance(client.extra, ExtraModules)
    assert isinstance(client.extra.link, LinkUtils)
    assert isinstance(client.extra.contract, ContractUtils)
    assert isinstance(client.extra.generators, GeneratorUtils)

    assert isinstance(client.account._client, Client)
    assert isinstance(client.block._client, Client)
    assert isinstance(client.contract._client, Client)
    assert isinstance(client.transaction._client, Client)
    assert isinstance(client.stats._client, Client)
    assert isinstance(client.logs._client, Client)
    assert isinstance(client.proxy._client, Client)

    assert isinstance(client.extra._client, Client)
    assert isinstance(client.extra.contract._client, Client)
    assert isinstance(client.extra.generators._client, Client)
    assert isinstance(client.extra.link._url_builder, UrlBuilder)


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


def test_api_kind(client):
    client._url_builder.api_kind = Mock()
    client._url_builder.api_kind.title = Mock()

    client.api_kind

    client._url_builder.api_kind.assert_not_called()
    client._url_builder.api_kind.title.assert_called_once()


def test_scaner_url(client):
    url = 'some_url'
    client._url_builder.BASE_URL = url
    assert client.scaner_url == url
