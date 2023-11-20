from datetime import date

from aioetherscan.common import check_sort_direction
from aioetherscan.modules.base import BaseModule


class GasTracker(BaseModule):
    """Gas Tracker

    https://docs.etherscan.io/api-endpoints/gas-tracker
    """

    @property
    def _module(self) -> str:
        return 'gastracker'

    async def estimation_of_confirmation_time(self, gas_price: int) -> str:
        """Get Estimation of Confirmation Time"""
        return await self._get(action='gasestimate', gasprice=gas_price)

    async def gas_oracle(self) -> dict:
        """Get Gas Oracle"""
        return await self._get(action='gasoracle')

    async def daily_average_gas_limit(
        self, start_date: date, end_date: date, sort: str | None = None
    ) -> list[dict]:
        """Get Daily Average Gas Limit"""
        return await self._get(
            module='stats',
            action='dailyavggaslimit',
            startdate=start_date.isoformat(),
            enddate=end_date.isoformat(),
            sort=check_sort_direction(sort),
        )

    async def daily_total_gas_used(
        self, start_date: date, end_date: date, sort: str | None = None
    ) -> dict:
        """Get Ethereum Daily Total Gas Used"""
        return await self._get(
            module='stats',
            action='dailygasused',
            startdate=start_date.isoformat(),
            enddate=end_date.isoformat(),
            sort=check_sort_direction(sort),
        )

    async def daily_average_gas_price(
        self, start_date: date, end_date: date, sort: str | None = None
    ) -> dict:
        """Get Daily Average Gas Price"""
        return await self._get(
            module='stats',
            action='dailyavggasprice',
            startdate=start_date.isoformat(),
            enddate=end_date.isoformat(),
            sort=check_sort_direction(sort),
        )
