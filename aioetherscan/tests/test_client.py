from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aioetherscan import Client
from aioetherscan.modules.account import Account
from aioetherscan.modules.block import Block
from aioetherscan.modules.contract import Contract
from aioetherscan.modules.logs import Logs
from aioetherscan.modules.proxy import Proxy
from aioetherscan.modules.stats import Stats
from aioetherscan.modules.transaction import Transaction
from aioetherscan.modules.utils import Utils


@pytest.fixture()
async def client():
    c = Client('TestApiKey')
    yield c
    await c.close()


def test_api_key():
    with pytest.raises(TypeError):
        c = Client()


def test_init(client):
    assert isinstance(client.account, Account)
    assert isinstance(client.block, Block)
    assert isinstance(client.contract, Contract)
    assert isinstance(client.transaction, Transaction)
    assert isinstance(client.stats, Stats)
    assert isinstance(client.logs, Logs)
    assert isinstance(client.proxy, Proxy)

    assert isinstance(client.utils, Utils)

    assert isinstance(client.account._client, Client)
    assert isinstance(client.block._client, Client)
    assert isinstance(client.contract._client, Client)
    assert isinstance(client.transaction._client, Client)
    assert isinstance(client.stats._client, Client)
    assert isinstance(client.logs._client, Client)
    assert isinstance(client.proxy._client, Client)

    assert isinstance(client.utils._client, Client)


@pytest.mark.asyncio
async def test_close_session(client):
    with patch('aioetherscan.network.Network.close', new_callable=CoroutineMock) as m:
        await client.close()
        m.assert_called_once_with()


@pytest.mark.asyncio
async def test_networks():
    with patch('aioetherscan.network.Network._set_network') as m:
        c = Client('TestApiKey')
        m.assert_called_once_with('eth', 'main')
        await c.close()

    with patch('aioetherscan.network.Network._set_network') as m:
        c = Client('TestApiKey', 'eth', 'kovan')
        m.assert_called_once_with('eth', 'kovan')
        await c.close()
#
