from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from aioetherscan import Client
from aioetherscan.exceptions import EtherscanClientApiError


@pytest_asyncio.fixture
async def contract_utils():
    c = Client('TestApiKey')
    yield c.extra.contract
    await c.close()


@pytest.mark.asyncio
async def test_is_contract_ok(contract_utils):
    return_value = {'some': 'data'}
    with patch(
        'aioetherscan.modules.contract.Contract.contract_abi',
        new=AsyncMock(return_value=return_value),
    ) as mock:
        result = await contract_utils.is_contract(address='addr')
        mock.assert_called_once_with(address='addr')
        assert result is True


@pytest.mark.asyncio
async def test_is_contract_negative(contract_utils):
    exc = EtherscanClientApiError(message='NOTOK', result='contract source code not verified')
    with patch(
        'aioetherscan.modules.contract.Contract.contract_abi', new=AsyncMock(side_effect=exc)
    ):
        result = await contract_utils.is_contract(address='addr')
        assert result is False


@pytest.mark.asyncio
async def test_is_contract_exception(contract_utils):
    exc = EtherscanClientApiError(message='some_msg', result='some_result')
    with patch(
        'aioetherscan.modules.contract.Contract.contract_abi', new=AsyncMock(side_effect=exc)
    ):
        with pytest.raises(EtherscanClientApiError):
            await contract_utils.is_contract(address='addr')


@pytest.mark.asyncio
async def test_get_contract_creator_internal_ok(contract_utils):
    creator = '0x123'
    internal_txs_mock = AsyncMock(
        return_value=[
            {'from': creator},
        ]
    )
    with patch('aioetherscan.modules.account.Account.internal_txs', new=internal_txs_mock) as mock:
        result = await contract_utils.get_contract_creator(contract_address='addr')
        mock.assert_called_once_with(address='addr', start_block=1, page=1, offset=1)
        assert result == creator


@pytest.mark.asyncio
async def test_get_contract_creator_internal_raise(contract_utils):
    exc = EtherscanClientApiError(message='No transactions found', result='')
    internal_txs_mock = AsyncMock(side_effect=exc)
    with patch('aioetherscan.modules.account.Account.internal_txs', new=internal_txs_mock):
        with pytest.raises(EtherscanClientApiError):
            await contract_utils.get_contract_creator(contract_address='addr')


@pytest.mark.asyncio
async def test_get_contract_creator_internal_raise_none(contract_utils):
    exc = EtherscanClientApiError(message='', result='')
    internal_txs_mock = AsyncMock(side_effect=exc)

    creator = '0x123'
    normal_txs_mock = AsyncMock(
        return_value=[
            {'from': creator},
        ]
    )
    with patch(
        'aioetherscan.modules.account.Account.internal_txs', new=internal_txs_mock
    ) as internal_mock:
        with patch(
            'aioetherscan.modules.account.Account.normal_txs', new=normal_txs_mock
        ) as normal_mock:
            result = await contract_utils.get_contract_creator(contract_address='addr')
            internal_mock.assert_called_once_with(address='addr', start_block=1, page=1, offset=1)
            normal_mock.assert_called_once_with(address='addr', start_block=1, page=1, offset=1)

            assert result == creator


@pytest.mark.asyncio
async def test_get_contract_creator_internal_raise_normal(contract_utils):
    exc = EtherscanClientApiError(message='', result='')
    internal_txs_mock = AsyncMock(side_effect=exc)

    normal_exc = EtherscanClientApiError(message='No transactions found', result='')
    normal_txs_mock = AsyncMock(side_effect=normal_exc)
    with patch('aioetherscan.modules.account.Account.internal_txs', new=internal_txs_mock):
        with patch('aioetherscan.modules.account.Account.normal_txs', new=normal_txs_mock):
            with pytest.raises(EtherscanClientApiError):
                await contract_utils.get_contract_creator(contract_address='addr')


@pytest.mark.asyncio
async def test_get_contract_creator_internal_none(contract_utils):
    empty_result_mock_int = AsyncMock(return_value=[])
    empty_result_mock_norm = AsyncMock(return_value=[])

    with patch(
        'aioetherscan.modules.account.Account.internal_txs', new=empty_result_mock_int
    ) as mock:
        with patch('aioetherscan.modules.account.Account.normal_txs', new=empty_result_mock_norm):
            result = await contract_utils.get_contract_creator(contract_address='addr')
            mock.assert_called_once_with(address='addr', start_block=1, page=1, offset=1)
            assert result is None
