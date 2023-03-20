from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from aioetherscan import Client


@pytest_asyncio.fixture
async def contract_utils():
    c = Client('TestApiKey')
    yield c.extra.contract
    await c.close()


@pytest.mark.asyncio
async def test_is_contract(contract_utils):
    with patch('aioetherscan.modules.contract.Contract.contract_abi', new=AsyncMock()) as mock:
        await contract_utils.is_contract(address='addr')
        mock.assert_called_once_with(address='addr')


@pytest.mark.asyncio
async def test_get_contract_creator(contract_utils):
    with patch('aioetherscan.modules.account.Account.internal_txs', new=AsyncMock()) as mock:
        await contract_utils.get_contract_creator(contract_address='addr')
        mock.assert_called_once_with(
            address='addr',
            start_block=1,
            page=1,
            offset=1
        )
