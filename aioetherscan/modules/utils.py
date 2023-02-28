from typing import Optional
from urllib.parse import urljoin, urlencode

from aioetherscan.exceptions import EtherscanClientApiError


class Utils:
    """Helper methods which use the combination of documented APIs."""

    def __init__(self, client):
        self._client = client
        self._BASE_URL = client._http.BASE_URL

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
            if e.message.lower() != 'no transactions found':
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
                if e.message.lower() != 'no transactions found':
                    raise

        return next((i['from'].lower() for i in response), None)

    def get_address_link(self, address: str) -> str:
        return urljoin(self._BASE_URL, f'address/{address}')

    def get_tx_link(self, tx_hash: str) -> str:
        return urljoin(self._BASE_URL, f'tx/{tx_hash}')

    def get_block_link(self, block_number: int) -> str:
        return urljoin(self._BASE_URL, f'block/{block_number}')

    def get_block_txs_link(self, block_number: int) -> str:
        return urljoin(self._BASE_URL, f'txs?{urlencode({"block": block_number})}')
