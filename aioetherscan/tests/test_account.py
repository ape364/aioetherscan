from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aioetherscan import Client


@pytest.fixture()
async def account():
    c = Client('TestApiKey')
    yield c.account
    await c.close()


@pytest.mark.asyncio
async def test_balance(account):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.balance('addr')
        mock.assert_called_once_with(params=dict(module='account', action='balance', address='addr', tag='latest'))

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.balance('addr', 123)
        mock.assert_called_once_with(params=dict(module='account', action='balance', address='addr', tag='0x7b'))


@pytest.mark.asyncio
async def test_balances(account):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.balances(['a1', 'a2'])
        mock.assert_called_once_with(
            params=dict(module='account', action='balancemulti', address='a1,a2', tag='latest'))

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.balances(['a1', 'a2'], 123)
        mock.assert_called_once_with(params=dict(module='account', action='balancemulti', address='a1,a2', tag='0x7b'))


@pytest.mark.asyncio
async def test_normal_txs(account):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.normal_txs('addr')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='txlist',
                address='addr',
                startblock=None,
                endblock=None,
                sort=None,
                page=None,
                offset=None
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.normal_txs(
            address='addr',
            start_block=1,
            end_block=2,
            sort='asc',
            page=3,
            offset=4
        )
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='txlist',
                address='addr',
                startblock=1,
                endblock=2,
                sort='asc',
                page=3,
                offset=4
            )
        )
    with pytest.raises(ValueError):
        await account.normal_txs(
            address='addr',
            sort='wrong',
        )


@pytest.mark.asyncio
async def test_internal_txs(account):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.internal_txs('addr')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='txlistinternal',
                address='addr',
                startblock=None,
                endblock=None,
                sort=None,
                page=None,
                offset=None,
                txhash=None
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.internal_txs(
            address='addr',
            start_block=1,
            end_block=2,
            sort='asc',
            page=3,
            offset=4,
            txhash='0x123'
        )
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='txlistinternal',
                address='addr',
                startblock=1,
                endblock=2,
                sort='asc',
                page=3,
                offset=4,
                txhash='0x123'
            )
        )
    with pytest.raises(ValueError):
        await account.internal_txs(
            address='addr',
            sort='wrong',
        )


@pytest.mark.asyncio
async def test_token_transfers(account):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.token_transfers('addr')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokentx',
                address='addr',
                startblock=None,
                endblock=None,
                sort=None,
                page=None,
                offset=None,
                contractaddress=None
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.token_transfers(contract_address='addr')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokentx',
                address=None,
                startblock=None,
                endblock=None,
                sort=None,
                page=None,
                offset=None,
                contractaddress='addr'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.token_transfers(
            address='addr',
            start_block=1,
            end_block=2,
            sort='asc',
            page=3,
            offset=4,
            contract_address='0x123'
        )
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokentx',
                address='addr',
                startblock=1,
                endblock=2,
                sort='asc',
                page=3,
                offset=4,
                contractaddress='0x123'
            )
        )

    with pytest.raises(ValueError):
        await account.token_transfers(
            address='addr',
            sort='wrong',
        )

    with pytest.raises(ValueError):
        await account.token_transfers()


@pytest.mark.asyncio
async def test_mined_blocks(account):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.mined_blocks('addr')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='getminedblocks',
                address='addr',
                blocktype='blocks',
                page=None,
                offset=None,
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.mined_blocks(
            address='addr',
            blocktype='uncles',
            page=1,
            offset=2
        )
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='getminedblocks',
                address='addr',
                blocktype='uncles',
                page=1,
                offset=2
            )
        )

    with pytest.raises(ValueError):
        await account.mined_blocks(
            address='addr',
            blocktype='wrong',
        )


@pytest.mark.asyncio
async def test_token_balance(account):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.token_balance('addr', 'contractaddr')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokenbalance',
                address='addr',
                contractaddress='contractaddr',
                tag='latest',
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await account.token_balance('addr', 'contractaddr', 123)
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokenbalance',
                address='addr',
                contractaddress='contractaddr',
                tag='0x7b',
            )
        )


def test_check(account):
    assert account._check('a', ('a', 'b')) == 'a'
    assert account._check('A', ('a', 'b')) == 'A'
    with pytest.raises(ValueError):
        account._check('c', ('a', 'b'))
    with pytest.raises(ValueError):
        account._check('C', ('a', 'b'))


def test_check_sort_direction(account):
    assert account._check_sort_direction('asc') == 'asc'
    assert account._check_sort_direction('desc') == 'desc'
    with pytest.raises(ValueError):
        account._check_sort_direction('wrong')


def test_check_blocktype(account):
    assert account._check_blocktype('blocks') == 'blocks'
    assert account._check_blocktype('uncles') == 'uncles'
    with pytest.raises(ValueError):
        account._check_blocktype('wrong')
