from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aioetherscan import Client


@pytest.fixture()
async def stats():
    c = Client('TestApiKey')
    yield c.stats
    await c.close()


@pytest.mark.asyncio
async def test_eth_supply(stats):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await stats.eth_supply()
        mock.assert_called_once_with(params=dict(module='stats', action='ethsupply'))


@pytest.mark.asyncio
async def test_eth_price(stats):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await stats.eth_price()
        mock.assert_called_once_with(params=dict(module='stats', action='ethprice'))
