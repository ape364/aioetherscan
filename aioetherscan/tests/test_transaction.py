from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aioetherscan import Client


@pytest.fixture()
async def transaction():
    c = Client('TestApiKey')
    yield c.transaction
    await c.close()


@pytest.mark.asyncio
async def test_contract_execution_status(transaction):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await transaction.contract_execution_status('0x123')
        mock.assert_called_once_with(params=dict(module='transaction', action='getstatus', txhash='0x123'))


@pytest.mark.asyncio
async def test_tx_receipt_status(transaction):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await transaction.tx_receipt_status('0x123')
        mock.assert_called_once_with(params=dict(module='transaction', action='gettxreceiptstatus', txhash='0x123'))
