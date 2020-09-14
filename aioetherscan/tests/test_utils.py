from unittest.mock import patch, call

import asynctest
import pytest
from asyncio_throttle import Throttler
from asynctest import CoroutineMock, MagicMock

from aioetherscan import Client
from aioetherscan.exceptions import EtherscanClientApiError


@pytest.fixture()
async def utils():
    c = Client('TestApiKey')
    yield c.utils
    await c.close()


@pytest.fixture()
async def throttler():
    t = Throttler(rate_limit=5)
    yield t


def test_generate_intervals(utils):
    expected = [(1, 3), (4, 6), (7, 9), (10, 10)]
    for i, j in utils._generate_intervals(1, 10, 3):
        assert (i, j) == expected.pop(0)

    expected = [(1, 2), (3, 4), (5, 6)]
    for i, j in utils._generate_intervals(1, 6, 2):
        assert (i, j) == expected.pop(0)

    for i, j in utils._generate_intervals(10, 0, 3):
        assert True == False  # not called


@pytest.mark.asyncio
async def test_parse_by_pages(utils, throttler):
    with patch('aioetherscan.modules.account.Account.token_transfers', new=CoroutineMock()) as transfers_mock:
        transfers_mock.side_effect = EtherscanClientApiError('No transactions found', None)
        async for _ in utils._parse_by_pages(
                100,
                200,
                5,
                address='address',
                contract_address='contract_address',
                throttler=throttler
        ):
            break
        transfers_mock.assert_called_once_with(
            address='address',
            contract_address='contract_address',
            start_block=100,
            end_block=200,
            page=1,
            offset=5
        )


@pytest.mark.asyncio
async def test_parse_by_pages_exception(utils, throttler):
    with patch('aioetherscan.modules.account.Account.token_transfers', new=CoroutineMock()) as transfers_mock:
        transfers_mock.side_effect = EtherscanClientApiError('other msg', None)
        try:
            async for _ in utils._parse_by_pages(
                    100,
                    200,
                    5,
                    address='address',
                    contract_address='contract_address',
                    throttler=throttler
            ):
                break
        except EtherscanClientApiError as e:
            assert e.message == 'other msg'


@pytest.mark.asyncio
async def test_parse_by_pages_result(utils, throttler):
    def token_transfers_side_effect_generator():
        yield [1]
        yield [2]
        raise EtherscanClientApiError('No transactions found', None)

    gen = token_transfers_side_effect_generator()

    def token_transfers_side_effect(**kwargs):
        for x in gen:
            return x

    with patch('aioetherscan.modules.account.Account.token_transfers', new=CoroutineMock()) as transfers_mock:
        transfers_mock.side_effect = token_transfers_side_effect

        i = 0
        res = []
        async for transfer in utils._parse_by_pages(
                100,
                200,
                5,
                address='address',
                contract_address='contract_address',
                throttler=throttler
        ):
            i += 1
            if i > 2:
                break
            res.append(transfer)
        transfers_mock.assert_has_calls(
            [
                call(
                    address='address',
                    contract_address='contract_address',
                    start_block=100,
                    end_block=200,
                    page=1,
                    offset=5
                ),
                call(
                    address='address',
                    contract_address='contract_address',
                    start_block=100,
                    end_block=200,
                    page=2,
                    offset=5
                ),
                call(
                    address='address',
                    contract_address='contract_address',
                    start_block=100,
                    end_block=200,
                    page=3,
                    offset=5
                ),
            ]
        )
        assert res == [1, 2]


@pytest.mark.asyncio
async def test_token_transfers(utils):
    with asynctest.patch(
            'aioetherscan.modules.utils.Utils.token_transfers_generator',
            new=MagicMock()
    ) as transfers_gen_mock:
        await utils.token_transfers(
            contract_address='contract_address'
        )
        transfers_gen_mock.assert_called_once_with(
            contract_address='contract_address',
            address=None,
            be_polite=True,
            block_limit=50,
            offset=3,
            start_block=0,
            end_block=None,
            throttler=None
        )


@pytest.mark.asyncio
async def test_token_transfers_generator(utils, throttler):
    with patch('aioetherscan.modules.utils.Utils._parse_by_pages', new=MagicMock()) as parse_mock:
        with patch('aioetherscan.modules.proxy.Proxy.block_number', new=CoroutineMock()) as proxy_mock:
            proxy_mock.return_value = '0x14'

            async for _ in utils.token_transfers_generator(address='addr', throttler=throttler):
                break

            parse_mock.assert_called_once_with(
                address='addr',
                contract_address=None,
                start_block=0,
                end_block=20,
                offset=3,
                throttler=throttler
            )

    with patch('aioetherscan.modules.utils.Utils._parse_by_pages', new=MagicMock()) as parse_mock:
        async for _ in utils.token_transfers_generator(
                contract_address='contract_address',
                end_block=20,
                throttler=throttler
        ):
            break

        parse_mock.assert_called_once_with(
            address=None,
            contract_address='contract_address',
            start_block=0,
            end_block=20,
            offset=3,
            throttler=throttler
        )


@pytest.mark.asyncio
async def test_one_of_addresses_is_supplied(utils):
    EXC_MESSAGE_RE = r'At least one of address or contract_address must be specified.'
    with pytest.raises(ValueError, match=EXC_MESSAGE_RE) as excinfo:
        async for _ in utils.token_transfers_generator(end_block=1):
            break


@pytest.mark.asyncio
async def test_is_contract(utils):
    with asynctest.patch('aioetherscan.modules.contract.Contract.contract_abi', new=CoroutineMock()) as mock:
        await utils.is_contract(address='addr')
        mock.assert_called_once_with(address='addr')


@pytest.mark.asyncio
async def test_get_contract_creator(utils):
    with asynctest.patch('aioetherscan.modules.account.Account.internal_txs', new=CoroutineMock()) as mock:
        await utils.get_contract_creator(contract_address='addr')
        mock.assert_called_once_with(
            address='addr',
            start_block=1,
            page=1,
            offset=1
        )
