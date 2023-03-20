from typing import Optional
from typing import TYPE_CHECKING

from aioetherscan.exceptions import EtherscanClientApiError

if TYPE_CHECKING:
    from aioetherscan import Client


class ContractUtils:
    """Helper methods which use the combination of documented APIs."""

    def __init__(self, client: 'Client'):
        self._client = client

    async def is_contract(self, address: str) -> bool:
        try:
            response = await self._client.contract.contract_abi(address=address)
        except EtherscanClientApiError as e:
            if e.message.upper() == 'NOTOK' and e.result.lower() == 'contract source code not verified':
                return False
            raise
        else:
            return True if response else False

    async def get_contract_creator(self, contract_address: str) -> Optional[str]:
        try:
            response = await self._client.account.internal_txs(
                address=contract_address,
                start_block=1,
                page=1,
                offset=1
            )  # try to find first internal transaction
        except EtherscanClientApiError as e:
            if e.message == 'No transactions found':
                raise
            else:
                response = None

        if not response:
            try:
                response = await self._client.account.normal_txs(
                    address=contract_address,
                    start_block=1,
                    page=1,
                    offset=1
                )  # try to find first normal transaction
            except EtherscanClientApiError as e:
                if e.message == 'No transactions found':
                    raise

        return next((i['from'].lower() for i in response), None)
