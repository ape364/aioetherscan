from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from aioetherscan import Client


@pytest_asyncio.fixture
async def account():
    c = Client('TestApiKey')
    yield c.account
    await c.close()


@pytest.mark.asyncio
async def test_balance(account):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await account.balance('addr')
        mock.assert_called_once_with(params=dict(module='account', action='balance', address='addr', tag='latest'))

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await account.balance('addr', 123)
        mock.assert_called_once_with(params=dict(module='account', action='balance', address='addr', tag='0x7b'))


@pytest.mark.asyncio
async def test_balances(account):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await account.balances(['a1', 'a2'])
        mock.assert_called_once_with(
            params=dict(module='account', action='balancemulti', address='a1,a2', tag='latest'))

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await account.balances(['a1', 'a2'], 123)
        mock.assert_called_once_with(params=dict(module='account', action='balancemulti', address='a1,a2', tag='0x7b'))


@pytest.mark.asyncio
async def test_normal_txs(account):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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
@pytest.mark.parametrize(
    'token_standard,expected_action',
    [
        ('erc20', 'tokentx'),
        ('erc721', 'tokennfttx'),
        ('erc1155', 'token1155tx'),
    ]
)
async def test_token_transfers(account, token_standard, expected_action):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await account.token_transfers(
            address='addr',
            start_block=1,
            end_block=2,
            sort='asc',
            page=3,
            offset=4,
            contract_address='0x123',
            token_standard=token_standard
        )
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action=expected_action,
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
        await account.token_transfers(start_block=123)


@pytest.mark.asyncio
async def test_mined_blocks(account):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
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
async def test_beacon_chain_withdrawals(account):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await account.beacon_chain_withdrawals('addr')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='txsBeaconWithdrawal',
                address='addr',
                startblock=None,
                endblock=None,
                sort=None,
                page=None,
                offset=None,
            )
        )

    with pytest.raises(ValueError):
        await account.beacon_chain_withdrawals(
            address='addr',
            sort='wrong',
        )


@pytest.mark.asyncio
async def test_account_balance_by_blockno(account):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await account.account_balance_by_blockno('a1', 123)
        mock.assert_called_once_with(
            params=dict(module='account', action='balancehistory', address='a1', blockno=123)
        )
