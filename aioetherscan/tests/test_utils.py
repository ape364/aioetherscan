from unittest.mock import patch, call

import asynctest
import pytest
from asynctest import CoroutineMock, MagicMock

from aioetherscan import Client
from aioetherscan.exceptions import EtherscanClientApiError


@pytest.fixture()
async def utils():
    c = Client('TestApiKey')
    yield c.utils
    await c.close()


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
async def test_parse_by_pages(utils):
    with patch('aioetherscan.modules.account.Account.token_transfers', new=CoroutineMock()) as transfers_mock:
        transfers_mock.side_effect = EtherscanClientApiError('No transactions found', None)
        await utils._parse_by_pages(
            'addr',
            100,
            200,
            5
        )
        transfers_mock.assert_called_once_with(
            contract_address='addr',
            start_block=100,
            end_block=200,
            page=1,
            offset=5
        )


@pytest.mark.asyncio
async def test_parse_by_pages_exception(utils):
    with patch('aioetherscan.modules.account.Account.token_transfers', new=CoroutineMock()) as transfers_mock:
        transfers_mock.side_effect = EtherscanClientApiError('other msg', None)
        try:
            await utils._parse_by_pages(
                'addr',
                100,
                200,
                5
            )
        except EtherscanClientApiError as e:
            assert e.message == 'other msg'


@pytest.mark.asyncio
async def test_parse_by_pages_result(utils):
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
        res = await utils._parse_by_pages(
            'addr',
            100,
            200,
            5
        )
        transfers_mock.assert_has_calls(
            [
                call(
                    contract_address='addr',
                    start_block=100,
                    end_block=200,
                    page=1,
                    offset=5
                ),
                call(
                    contract_address='addr',
                    start_block=100,
                    end_block=200,
                    page=2,
                    offset=5
                ),
                call(
                    contract_address='addr',
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
            contract_address='addr'
        )
        transfers_gen_mock.assert_called_once_with(
            contract_address='addr',
            be_polite=True,
            block_limit=50,
            offset=3,
            start_block=0,
            end_block=None
        )


@pytest.mark.asyncio
async def test_token_transfers_generator(utils):
    with patch('aioetherscan.modules.utils.Utils._parse_by_pages', new=CoroutineMock()) as parse_mock:
        with patch('aioetherscan.modules.proxy.Proxy.block_number', new=CoroutineMock()) as proxy_mock:
            proxy_mock.return_value = '0x14'

            async for _ in utils.token_transfers_generator('addr'):
                break

            parse_mock.assert_called_once_with('addr', 0, 20, 3)

    with patch('aioetherscan.modules.utils.Utils._parse_by_pages', new=CoroutineMock()) as parse_mock:
        with patch('aioetherscan.modules.proxy.Proxy.block_number', new=CoroutineMock()) as proxy_mock:
            with patch('asyncio.gather', new=CoroutineMock()) as asyncio_mock:
                proxy_mock.return_value = '0x14'

                async for _ in utils.token_transfers_generator('addr', be_polite=False):
                    break

                parse_mock.assert_called_once_with('addr', 0, 20, 3)
                asyncio_mock.assert_called_once()

    with patch('aioetherscan.modules.utils.Utils._parse_by_pages', new=CoroutineMock()) as parse_mock:
        async for _ in utils.token_transfers_generator('addr', end_block=20):
            break

        parse_mock.assert_called_once_with('addr', 0, 20, 3)


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
