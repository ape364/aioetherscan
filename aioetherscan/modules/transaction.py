from typing import Dict

from aioetherscan.modules.base import BaseModule


class Transaction(BaseModule):
    """Transaction APIs

    https://etherscan.io/apis#transactions
    """

    @property
    def _module(self) -> str:
        return 'transaction'

    async def contract_execution_status(self, txhash: str) -> Dict:
        """[BETA] Check Contract Execution Status (if there was an error during contract execution) """
        return await self._get(
            action='getstatus',
            txhash=txhash
        )

    async def tx_receipt_status(self, txhash: str) -> Dict:
        """[BETA] Check Transaction Receipt Status (Only applicable for Post Byzantium fork transactions) """
        return await self._get(
            action='gettxreceiptstatus',
            txhash=txhash
        )
