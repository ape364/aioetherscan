from typing import Dict

from aioetherscan.modules.base import BaseModule


class Stats(BaseModule):
    """General stats

    https://etherscan.io/apis#stats
    """

    @property
    def _module(self) -> str:
        return 'stats'

    async def eth_supply(self) -> str:
        """Get Total Supply of Ether"""
        return await self._get(action='ethsupply')

    async def eth_price(self) -> Dict:
        """Get ETHER LastPrice Price"""
        return await self._get(action='ethprice')
