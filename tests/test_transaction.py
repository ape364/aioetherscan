from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from aioetherscan import Client


@pytest_asyncio.fixture
async def transaction():
    c = Client('TestApiKey')
    yield c.transaction
    await c.close()


@pytest.mark.asyncio
async def test_contract_execution_status(transaction):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await transaction.contract_execution_status('0x123')
        mock.assert_called_once_with(params=dict(module='transaction', action='getstatus', txhash='0x123'))


@pytest.mark.asyncio
async def test_tx_receipt_status(transaction):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await transaction.tx_receipt_status('0x123')
        mock.assert_called_once_with(params=dict(module='transaction', action='gettxreceiptstatus', txhash='0x123'))
