from datetime import date
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio

from aioetherscan import Client


@pytest_asyncio.fixture
async def stats():
    c = Client('TestApiKey')
    yield c.stats
    await c.close()


@pytest.mark.asyncio
async def test_eth_supply(stats):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.eth_supply()
        mock.assert_called_once_with(params=dict(module='stats', action='ethsupply'))


@pytest.mark.asyncio
async def test_eth2_supply(stats):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.eth2_supply()
        mock.assert_called_once_with(params=dict(module='stats', action='ethsupply2'))


@pytest.mark.asyncio
async def test_eth_price(stats):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.eth_price()
        mock.assert_called_once_with(params=dict(module='stats', action='ethprice'))


@pytest.mark.asyncio
async def test_eth_nodes_size(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.eth_nodes_size(start_date, end_date, 'geth', 'default', 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='chainsize',
                startdate='2023-11-12',
                enddate='2023-11-13',
                clienttype='geth',
                syncmode='default',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.eth_nodes_size(
            start_date,
            end_date,
            'geth',
            'default',
        )
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='chainsize',
                startdate='2023-11-12',
                enddate='2023-11-13',
                clienttype='geth',
                syncmode='default',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.eth_nodes_size(start_date, end_date, 'wrong', 'default', 'asc')

    with pytest.raises(ValueError):
        await stats.eth_nodes_size(start_date, end_date, 'geth', 'wrong', 'asc')

    with pytest.raises(ValueError):
        await stats.eth_nodes_size(start_date, end_date, 'geth', 'default', 'wrong')


@pytest.mark.asyncio
async def test_total_nodes_count(stats):
    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.total_nodes_count()
        mock.assert_called_once_with(params=dict(module='stats', action='nodecount'))


@pytest.mark.asyncio
async def test_daily_network_tx_fee(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_network_tx_fee(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailytxnfee',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_network_tx_fee(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailytxnfee',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.daily_network_tx_fee(start_date, end_date, 'wrong')


@pytest.mark.asyncio
async def test_daily_new_address_count(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_new_address_count(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailynewaddress',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_new_address_count(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailynewaddress',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.daily_new_address_count(start_date, end_date, 'wrong')


@pytest.mark.asyncio
async def test_daily_network_utilization(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_network_utilization(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailynetutilization',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_network_utilization(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailynetutilization',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.daily_network_utilization(start_date, end_date, 'wrong')


@pytest.mark.asyncio
async def test_daily_average_network_hash_rate(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_average_network_hash_rate(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailyavghashrate',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_average_network_hash_rate(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailyavghashrate',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.daily_average_network_hash_rate(start_date, end_date, 'wrong')


@pytest.mark.asyncio
async def test_daily_transaction_count(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_transaction_count(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailytx',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_transaction_count(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailytx',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.daily_transaction_count(start_date, end_date, 'wrong')


@pytest.mark.asyncio
async def test_daily_average_network_difficulty(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_average_network_difficulty(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailyavgnetdifficulty',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.daily_average_network_difficulty(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='dailyavgnetdifficulty',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.daily_average_network_difficulty(start_date, end_date, 'wrong')


@pytest.mark.asyncio
async def test_ether_historical_daily_market_cap(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.ether_historical_daily_market_cap(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='ethdailymarketcap',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.ether_historical_daily_market_cap(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='ethdailymarketcap',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.ether_historical_daily_market_cap(start_date, end_date, 'wrong')


@pytest.mark.asyncio
async def test_ether_historical_price(stats):
    start_date = date(2023, 11, 12)
    end_date = date(2023, 11, 13)

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.ether_historical_price(start_date, end_date, 'asc')
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='ethdailyprice',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort='asc',
            )
        )

    with patch('aioetherscan.network.Network.get', new=AsyncMock()) as mock:
        await stats.ether_historical_price(start_date, end_date)
        mock.assert_called_once_with(
            params=dict(
                module='stats',
                action='ethdailyprice',
                startdate='2023-11-12',
                enddate='2023-11-13',
                sort=None,
            )
        )

    with pytest.raises(ValueError):
        await stats.ether_historical_price(start_date, end_date, 'wrong')
