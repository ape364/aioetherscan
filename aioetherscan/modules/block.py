from typing import Dict

from aioetherscan.modules.base import BaseModule


class Block(BaseModule):
    """Block APIs

    https://etherscan.io/apis#blocks
    """

    @property
    def _module(self) -> str:
        return 'block'

    async def block_reward(self, blockno: int) -> Dict:
        """[BETA] Get Block And Uncle Rewards by BlockNo."""
        return await self._get(
            action='getblockreward',
            blockno=blockno
        )
