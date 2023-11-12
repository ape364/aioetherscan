from typing import Dict

from aioetherscan.common import check_closest_value
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
