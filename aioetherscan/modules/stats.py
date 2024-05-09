from datetime import date
from typing import Dict, Optional

from aioetherscan.common import check_client_type, check_sync_mode, get_daily_stats_params
from aioetherscan.modules.base import BaseModule


class Stats(BaseModule):
    """Stats

    https://docs.etherscan.io/api-endpoints/stats-1
    """

    @property
    def _module(self) -> str:
        return 'stats'

    async def eth_supply(self) -> str:
        """Get Total Supply of Ether"""
        return await self._get(action='ethsupply')

    async def eth2_supply(self) -> str:
        """Get Total Supply of Ether"""
        return await self._get(action='ethsupply2')

    async def eth_price(self) -> Dict:
        """Get ETHER LastPrice Price"""
        return await self._get(action='ethprice')

    async def eth_nodes_size(
        self,
        start_date: date,
        end_date: date,
        client_type: str,
        sync_mode: str,
        sort: Optional[str] = None,
    ) -> Dict:
        """Get Ethereum Nodes Size"""
        return await self._get(
            **get_daily_stats_params('chainsize', start_date, end_date, sort),
            clienttype=check_client_type(client_type),
            syncmode=check_sync_mode(sync_mode),
        )

    async def total_nodes_count(self) -> Dict:
        """Get Total Nodes Count"""
        return await self._get(action='nodecount')

    async def daily_network_tx_fee(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Daily Network Transaction Fee"""
        return await self._get(**get_daily_stats_params('dailytxnfee', start_date, end_date, sort))

    async def daily_new_address_count(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Daily New Address Count"""
        return await self._get(
            **get_daily_stats_params('dailynewaddress', start_date, end_date, sort)
        )

    async def daily_network_utilization(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Daily Network Utilization"""
        return await self._get(
            **get_daily_stats_params('dailynetutilization', start_date, end_date, sort)
        )

    async def daily_average_network_hash_rate(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Daily Average Network Hash Rate"""
        return await self._get(
            **get_daily_stats_params('dailyavghashrate', start_date, end_date, sort)
        )

    async def daily_transaction_count(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Daily Transaction Count"""
        return await self._get(**get_daily_stats_params('dailytx', start_date, end_date, sort))

    async def daily_average_network_difficulty(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Daily Average Network Difficulty"""
        return await self._get(
            **get_daily_stats_params('dailyavgnetdifficulty', start_date, end_date, sort)
        )

    async def ether_historical_daily_market_cap(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Ether Historical Daily Market Cap"""
        return await self._get(
            **get_daily_stats_params('ethdailymarketcap', start_date, end_date, sort)
        )

    async def ether_historical_price(
        self, start_date: date, end_date: date, sort: Optional[str] = None
    ) -> Dict:
        """Get Ether Historical Price"""
        return await self._get(
            **get_daily_stats_params('ethdailyprice', start_date, end_date, sort)
        )
