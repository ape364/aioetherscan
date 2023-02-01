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


@pytest.mark.parametrize(
    "api_kind,network_name,address,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/address/qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/address/qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/address/qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/address/qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/address/qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/address/qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/address/qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/address/qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/address/qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/address/qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/address/qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/address/qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/address/qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/address/qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/address/qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/address/qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/address/qwe'),
    ]
)
def test_get_address_link(api_kind, network_name, address, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_address_link(address) == expected


@pytest.mark.parametrize(
    "api_kind,network_name,tx_hash,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/tx/qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/tx/qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/tx/qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/tx/qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/tx/qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/tx/qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/tx/qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/tx/qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/tx/qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/tx/qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/tx/qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/tx/qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/tx/qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/tx/qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/tx/qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/tx/qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/tx/qwe'),
    ]
)
def test_get_tx_link(api_kind, network_name, tx_hash, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_tx_link(tx_hash) == expected


@pytest.mark.parametrize(
    "api_kind,network_name,block_number,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/block/qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/block/qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/block/qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/block/qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/block/qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/block/qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/block/qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/block/qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/block/qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/block/qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/block/qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/block/qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/block/qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/block/qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/block/qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/block/qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/block/qwe'),
    ]
)
def test_get_block_link(api_kind, network_name, block_number, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_block_link(block_number) == expected


@pytest.mark.parametrize(
    "api_kind,network_name,block_number,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/txs?block=qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/txs?block=qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/txs?block=qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/txs?block=qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/txs?block=qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/txs?block=qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/txs?block=qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/txs?block=qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/txs?block=qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/txs?block=qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/txs?block=qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/txs?block=qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/txs?block=qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/txs?block=qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/txs?block=qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/txs?block=qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/txs?block=qwe'),
    ]
)
def test_get_block_txs_link(api_kind, network_name, block_number, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_block_txs_link(block_number) == expected
