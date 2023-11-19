from datetime import date
from typing import Dict, Optional

from aioetherscan.common import check_closest_value, check_sort_direction
from aioetherscan.modules.base import BaseModule


class Block(BaseModule):
    """Blocks

    https://docs.etherscan.io/api-endpoints/blocks
    """

    @property
    def _module(self) -> str:
        return 'block'

    async def block_reward(self, blockno: int) -> Dict:
        """Get Block And Uncle Rewards by BlockNo"""
        return await self._get(
            action='getblockreward',
            blockno=blockno
        )

    async def est_block_countdown_time(self, blockno: int) -> Dict:
        """Get Estimated Block Countdown Time by BlockNo"""
        return await self._get(
            action='getblockcountdown',
            blockno=blockno
        )

    async def block_number_by_ts(self, ts: int, closest: str) -> Dict:
        """Get Block Number by Timestamp"""
        return await self._get(
            action='getblocknobytime',
            timestamp=ts,
            closest=check_closest_value(closest)
        )

    async def _get_daily_stats(self, action: str, start_date: date, end_date: date, sort: str) -> Dict:
        return await self._get(
            module='stats',
            action=action,
            startdate=start_date.isoformat(),
            enddate=end_date.isoformat(),
            sort=check_sort_direction(sort)
        )

    async def daily_average_block_size(self, start_date: date, end_date: date, sort: Optional[str] = None) -> Dict:
        """Get Daily Average Block Size"""
        return await self._get_daily_stats('dailyavgblocksize', start_date, end_date, sort)

    async def daily_block_count(self, start_date: date, end_date: date, sort: Optional[str] = None) -> Dict:
        """Get Daily Block Count and Rewards"""
        return await self._get_daily_stats('dailyblkcount', start_date, end_date, sort)

    async def daily_block_rewards(self, start_date: date, end_date: date, sort: Optional[str] = None) -> Dict:
        """Get Daily Block Rewards"""
        return await self._get_daily_stats('dailyblockrewards', start_date, end_date, sort)

    async def daily_average_time_for_a_block(self, start_date: date, end_date: date,
                                             sort: Optional[str] = None) -> Dict:
        """Get Daily Average Time for A Block to be Included in the Ethereum Blockchain"""
        return await self._get_daily_stats('dailyavgblocktime', start_date, end_date, sort)

    async def daily_uncle_block_count(self, start_date: date, end_date: date, sort: Optional[str] = None) -> Dict:
        """Get Daily Uncle Block Count and Rewards"""
        return await self._get_daily_stats('dailyuncleblkcount', start_date, end_date, sort)
