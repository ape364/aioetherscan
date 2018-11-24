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
