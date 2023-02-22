from unittest.mock import patch, call
from itertools import count

import asynctest
import pytest
from asynctest import CoroutineMock, MagicMock

from aioetherscan import Client
from aioetherscan.exceptions import EtherscanClientApiError


@pytest.fixture()
async def client():
    c = Client('TestApiKey')
    yield c
    await c.close()


@pytest.fixture()
async def utils(client):
    yield client.utils


@pytest.fixture()
async def account_proxy(client):
    yield client.utils.account_proxy


def test_generate_intervals(account_proxy):
    expected = [(1, 3), (4, 6), (7, 9), (10, 10)]
    for i, j in account_proxy.generate_intervals(1, 10, 3):
        assert (i, j) == expected.pop(0)

    expected = [(1, 2), (3, 4), (5, 6)]
    for i, j in account_proxy.generate_intervals(1, 6, 2):
        assert (i, j) == expected.pop(0)

    for i, j in account_proxy.generate_intervals(10, 0, 3):
        assert True == False  # not called


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
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/address/qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/address/qwe'),
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
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/tx/qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/tx/qwe'),
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
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/block/qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/block/qwe'),
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
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/txs?block=qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/txs?block=qwe'),
    ]
)
def test_get_block_txs_link(api_kind, network_name, block_number, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_block_txs_link(block_number) == expected


class TestBaseProxy:
    @pytest.mark.asyncio
    async def test_proxy(self, account_proxy):
        mock = CoroutineMock(return_value=[1, 2])
        actual = [v async for v in account_proxy.proxy(mock)(
            'foo',
            test='bar',
        )]

        mock.assert_awaited_once_with('foo', test='bar')
        assert actual == [1, 2]

    @pytest.mark.asyncio
    async def test_proxy_empty_result(self, account_proxy):
        mock = CoroutineMock(side_effect=EtherscanClientApiError(
            'No transactions found', None))
        with pytest.raises(EtherscanClientApiError, match=r"\[No transactions found\] None"):
            async for _ in account_proxy.proxy(mock)(
                'foo',
                test='bar',
            ):
                pass

        mock.assert_awaited_once_with('foo', test='bar')

    @pytest.mark.asyncio
    async def test_proxy_exception(self, account_proxy):
        mock = CoroutineMock(
            side_effect=EtherscanClientApiError('Error', None))
        with pytest.raises(EtherscanClientApiError, match=r"\[Error\] None"):
            async for _ in account_proxy.proxy(mock)(
                'foo',
                test='bar',
            ):
                pass

        mock.assert_called_once_with('foo', test='bar')

    @pytest.mark.asyncio
    @pytest.mark.parametrize("stop_if_empty", [False, True])
    async def test_parametrize_exception(self, account_proxy, stop_if_empty):
        def side_effect_generator():
            yield EtherscanClientApiError('Another error', None)
            yield []  # Should not reach this line

        mock = CoroutineMock(side_effect=side_effect_generator())

        @account_proxy.parametrize("page", range(1, 3), stop_if_empty=stop_if_empty)
        async def _proxy(*arg, **kwarg):
            async for v in account_proxy.proxy(mock)(*arg, **kwarg):
                yield v

        with pytest.raises(EtherscanClientApiError, match=r"\[Another error\] None"):
            async for _ in _proxy(
                'foo',
                test='bar',
            ):
                pass

        mock.assert_awaited_once_with('foo', test='bar', page=1)

    @pytest.mark.asyncio
    async def test_parametrize_stop_if_empty(self, account_proxy):
        def side_effect_generator():
            yield []
            yield []
            yield EtherscanClientApiError('No transactions found', None)
            yield []

        mock = CoroutineMock(side_effect=side_effect_generator())

        @account_proxy.parametrize("page", count(1))
        async def _proxy(*arg, **kwarg):
            async for v in account_proxy.proxy(mock)(*arg, **kwarg):
                yield v

        async for _ in _proxy(
            'foo',
            test='bar',
        ):
            pass
        assert mock.await_count == 3
        mock.assert_has_awaits([
            call('foo', test='bar', page=1),
            call('foo', test='bar', page=2),
            call('foo', test='bar', page=3),
        ])

    @pytest.mark.asyncio
    async def test_parametrize_ignore_error(self, account_proxy):
        def side_effect_generator():
            yield []
            yield []
            yield EtherscanClientApiError('No transactions found', None)
            yield []
            yield []  # Should not reach this line

        mock = CoroutineMock(side_effect=side_effect_generator())

        @account_proxy.parametrize("page", range(1, 5), stop_if_empty=False)
        async def _proxy(*arg, **kwarg):
            async for v in account_proxy.proxy(mock)(*arg, **kwarg):
                yield v

        async for _ in _proxy(
            'foo',
            test='bar',
        ):
            pass
        assert mock.await_count == 4
        mock.assert_has_awaits([
            call('foo', test='bar', page=1),
            call('foo', test='bar', page=2),
            call('foo', test='bar', page=3),
            call('foo', test='bar', page=4),
        ])

    @pytest.mark.asyncio
    async def test_parse_by_pages(self, account_proxy):
        def side_effect_generator():
            yield [1, 2]
            yield [3]
            yield EtherscanClientApiError('No transactions found', None)
            yield [4]

        mock = CoroutineMock(side_effect=side_effect_generator())

        result = [v async for v in account_proxy.parse_by_pages(
            mock,
            'foo',
            test='bar',
        )]
        assert mock.await_count == 3
        mock.assert_has_awaits([
            call('foo', test='bar', page=1),
            call('foo', test='bar', page=2),
            call('foo', test='bar', page=3),
        ])
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_parse_by_blocks(self, account_proxy):
        def side_effect_generator():
            yield [1, 2]
            yield [3]
            yield EtherscanClientApiError('No transactions found', None)
            yield [4]
            yield EtherscanClientApiError('No transactions found', None)

        mock = CoroutineMock(side_effect=side_effect_generator())

        with asynctest.patch(
            'aioetherscan.modules.proxy.Proxy.block_number',
            new=CoroutineMock(return_value="0x5")
        ):
            result = [v async for v in account_proxy.parse_by_blocks(
                mock,
                'foo',
                test='bar',
                start_block=2,
                end_block=None,
                block_limit=2,
            )]
        assert mock.await_count == 5
        mock.assert_has_awaits([
            call('foo', test='bar', start_block=2, end_block=3, page=1),
            call('foo', test='bar', start_block=2, end_block=3, page=2),
            call('foo', test='bar', start_block=2, end_block=3, page=3),
            call('foo', test='bar', start_block=4, end_block=5, page=1),
            call('foo', test='bar', start_block=4, end_block=5, page=2),
        ])
        assert result == [1, 2, 3, 4]


class TestAccountProxy:
    @pytest.mark.asyncio
    async def test_mined_blocks_generator(self, client, account_proxy):
        mock = MagicMock()
        with asynctest.patch(
            'aioetherscan.modules.utils.BaseProxy.parse_by_pages',
            new=mock
        ):
            async for v in account_proxy.mined_blocks_generator(
                address="address",
                blocktype='blocks',
                page=1,
                offset=10_000,
            ):
                pass
            mock.assert_called_once_with(
                client.account.mined_blocks,
                address="address",
                blocktype='blocks',
                page=1,
                offset=10_000,
            )

    @pytest.mark.asyncio
    async def test_normal_txs_generator(self, client, account_proxy):
        mock = MagicMock()
        with asynctest.patch(
            'aioetherscan.modules.utils.BaseProxy.parse_by_blocks',
            new=mock
        ):
            async for v in account_proxy.normal_txs_generator(
                address="address",
                start_block=0,
                end_block=None,
                sort="asc",
                page=1,
                offset=10_000,
            ):
                pass
            mock.assert_called_once_with(
                client.account.normal_txs,
                address="address",
                start_block=0,
                end_block=None,
                sort="asc",
                page=1,
                offset=10_000,
            )

    @pytest.mark.asyncio
    async def test_internal_txs_generator(self, client, account_proxy):
        mock = MagicMock()
        with asynctest.patch(
            'aioetherscan.modules.utils.BaseProxy.parse_by_blocks',
            new=mock
        ):
            async for v in account_proxy.internal_txs_generator(
                address="address",
                start_block=0,
                end_block=None,
                sort="asc",
                page=1,
                offset=10_000,
                txhash="0x",
            ):
                pass
            mock.assert_called_once_with(
                client.account.internal_txs,
                address="address",
                start_block=0,
                end_block=None,
                sort="asc",
                page=1,
                offset=10_000,
                txhash="0x",
            )

    @pytest.mark.asyncio
    async def test_token_transfers_generator(self, client, account_proxy):
        mock = MagicMock()
        with asynctest.patch(
            'aioetherscan.modules.utils.BaseProxy.parse_by_blocks',
            new=mock
        ):
            async for v in account_proxy.token_transfers_generator(
                address="address",
                start_block=0,
                end_block=None,
                sort="asc",
                page=1,
                offset=10_000,
            ):
                pass
            mock.assert_called_once_with(
                client.account.token_transfers,
                address="address",
                start_block=0,
                end_block=None,
                sort="asc",
                page=1,
                offset=10_000,
            )

    @pytest.mark.asyncio
    async def test_one_of_addresses_is_supplied(self, account_proxy):
        EXC_MESSAGE_RE = r'At least one of address or contract_address must be specified.'
        with pytest.raises(ValueError, match=EXC_MESSAGE_RE):
            async for _ in account_proxy.token_transfers_generator(end_block=1):
                break
