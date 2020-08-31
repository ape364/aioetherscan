from typing import Iterable, Optional, List, Dict

from aioetherscan.common import check_tag
from aioetherscan.modules.base import BaseModule


class Account(BaseModule):
    """Account & token APIs

    https://etherscan.io/apis#accounts
    https://etherscan.io/apis#tokens
    """

    _SORT_ORDERS = (
        'asc',  # ascending order
        'desc'  # descending order
    )

    _BLOCK_TYPES = (
        'blocks',  # full blocks only
        'uncles'  # uncle blocks only
    )

    @property
    def _module(self) -> str:
        return 'account'

    async def balance(self, address: str, tag: str = 'latest') -> str:
        """Get Ether Balance for a single Address."""
        return await self._get(
            action='balance',
            address=address,
            tag=check_tag(tag)
        )

    async def balances(self, addresses: Iterable[str], tag: str = 'latest') -> List[Dict]:
        """Get Ether Balance for multiple Addresses in a single call."""
        return await self._get(
            action='balancemulti',
            address=','.join(addresses),
            tag=check_tag(tag)
        )

    async def normal_txs(
            self,
            address: str,
            start_block: Optional[int] = None,
            end_block: Optional[int] = None,
            sort: Optional[str] = None,
            page: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[Dict]:
        """Get a list of 'Normal' Transactions By Address."""
        return await self._get(
            action='txlist',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort=self._check_sort_direction(sort),
            page=page,
            offset=offset
        )

    async def internal_txs(
            self,
            address: str,
            start_block: Optional[int] = None,
            end_block: Optional[int] = None,
            sort: Optional[str] = None,
            page: Optional[int] = None,
            offset: Optional[int] = None,
            txhash: Optional[str] = None
    ) -> List[Dict]:
        """Get a list of 'Internal' Transactions by Address or Transaction Hash."""
        return await self._get(
            action='txlistinternal',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort=self._check_sort_direction(sort),
            page=page,
            offset=offset,
            txhash=txhash
        )

    async def token_transfers(
            self,
            address: Optional[str] = None,
            contract_address: Optional[str] = None,
            start_block: Optional[int] = None,
            end_block: Optional[int] = None,
            sort: Optional[str] = None,
            page: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> List[Dict]:
        """Get a list of "ERC20 - Token Transfer Events" by Address."""
        if not address and not contract_address:
            raise ValueError('At least one of address or contract_address must be specified.')

        return await self._get(
            action='tokentx',
            address=address,
            startblock=start_block,
            endblock=end_block,
            sort=self._check_sort_direction(sort),
            page=page,
            offset=offset,
            contractaddress=contract_address
        )

    async def mined_blocks(
            self,
            address: str,
            blocktype: str = 'blocks',
            page: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List:
        """Get list of Blocks Mined by Address."""
        return await self._get(
            action='getminedblocks',
            address=address,
            blocktype=self._check_blocktype(blocktype),
            page=page,
            offset=offset
        )

    async def token_balance(self, address: str, contract_address: str, tag: str = 'latest') -> str:
        """Get ERC20-Token Account Balance for TokenContractAddress."""
        return await self._get(
            action='tokenbalance',
            address=address,
            contractaddress=contract_address,
            tag=check_tag(tag)
        )

    def _check_sort_direction(self, sort: str) -> str:
        return self._check(sort, self._SORT_ORDERS)

    def _check_blocktype(self, blocktype: str) -> str:
        return self._check(blocktype, self._BLOCK_TYPES)
