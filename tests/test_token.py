from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from aioetherscan import Client


@pytest_asyncio.fixture
async def token():
    c = Client('TestApiKey')
    yield c.token
    await c.close()


@pytest.mark.asyncio
async def test_total_supply(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.total_supply('addr')
        mock.assert_called_once_with(
            params=dict(module='stats', action='tokensupply', contractaddress='addr')
        )


@pytest.mark.asyncio
async def test_account_balance(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.account_balance('a1', 'c1')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokenbalance',
                address='a1',
                contractaddress='c1',
                tag='latest',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.account_balance('a1', 'c1', 123)
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokenbalance',
                address='a1',
                contractaddress='c1',
                tag='0x7b',
            )
        )


@pytest.mark.asyncio
async def test_total_supply_by_blockno(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.total_supply_by_blockno('c1', 123)
        mock.assert_called_once_with(
            params=dict(
                module='stats', action='tokensupplyhistory', contractaddress='c1', blockno=123
            )
        )


@pytest.mark.asyncio
async def test_account_balance_by_blockno(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.account_balance_by_blockno('a1', 'c1', 123)
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='tokenbalancehistory',
                address='a1',
                contractaddress='c1',
                blockno=123,
            )
        )


@pytest.mark.asyncio
async def test_token_holder_list(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_holder_list('c1')
        mock.assert_called_once_with(
            params=dict(
                module='token',
                action='tokenholderlist',
                contractaddress='c1',
                page=None,
                offset=None,
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_holder_list('c1', 1, 10)
        mock.assert_called_once_with(
            params=dict(
                module='token', action='tokenholderlist', contractaddress='c1', page=1, offset=10
            )
        )


@pytest.mark.asyncio
async def test_token_info(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_info('c1')
        mock.assert_called_once_with(
            params=dict(module='token', action='tokeninfo', contractaddress='c1')
        )


@pytest.mark.asyncio
async def test_token_holding_erc20(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_holding_erc20('a1')
        mock.assert_called_once_with(
            params=dict(
                module='account', action='addresstokenbalance', address='a1', page=None, offset=None
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_holding_erc20('a1', 1, 10)
        mock.assert_called_once_with(
            params=dict(
                module='account', action='addresstokenbalance', address='a1', page=1, offset=10
            )
        )


@pytest.mark.asyncio
async def test_token_holding_erc721(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_holding_erc721('a1')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='addresstokennftbalance',
                address='a1',
                page=None,
                offset=None,
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_holding_erc721('a1', 1, 10)
        mock.assert_called_once_with(
            params=dict(
                module='account', action='addresstokennftbalance', address='a1', page=1, offset=10
            )
        )


@pytest.mark.asyncio
async def test_token_inventory(token):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_inventory('a1', 'c1')
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='addresstokennftinventory',
                address='a1',
                contractaddress='c1',
                page=None,
                offset=None,
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await token.token_inventory('a1', 'c1', 1, 10)
        mock.assert_called_once_with(
            params=dict(
                module='account',
                action='addresstokennftinventory',
                address='a1',
                contractaddress='c1',
                page=1,
                offset=10,
            )
        )
