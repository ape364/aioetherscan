from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aioetherscan import Client


@pytest.fixture()
async def block():
    c = Client('TestApiKey')
    yield c.block
    await c.close()


@pytest.mark.asyncio
async def test_block_reward(block):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await block.block_reward(123)
        mock.assert_called_once_with(params=dict(module='block', action='getblockreward', blockno=123))


@pytest.mark.asyncio
async def test_est_block_countdown_time(block):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await block.est_block_countdown_time(123)
        mock.assert_called_once_with(params=dict(module='block', action='getblockcountdown', blockno=123))


@pytest.mark.asyncio
async def test_block_number_by_ts(block):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await block.block_number_by_ts(123, 'before')
        mock.assert_called_once_with(
            params=dict(module='block', action='getblocknobytime', timestamp=123, closest='before'))

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await block.block_number_by_ts(321, 'after')
        mock.assert_called_once_with(
            params=dict(module='block', action='getblocknobytime', timestamp=321, closest='after'))

    with pytest.raises(ValueError):
        await block.block_number_by_ts(
            ts=111,
            closest='wrong',
        )
