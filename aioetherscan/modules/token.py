from typing import Dict, List

from aioetherscan.common import check_tag
from aioetherscan.modules.base import BaseModule


class Token(BaseModule):
    """Tokens

    https://docs.etherscan.io/api-endpoints/tokens
    """

    @property
    def _module(self) -> str:
        return 'token'

    async def total_supply(self, contract_address: str) -> str:
        """Get ERC20-Token TotalSupply by ContractAddress"""
        return await self._get(
            module='stats',
            action='tokensupply',
            contractaddress=contract_address,
        )

    async def account_balance(
        self, address: str, contract_address: str, tag: str = 'latest'
    ) -> str:
        """Get ERC20-Token Account Balance for TokenContractAddress"""
        return await self._get(
            module='account',
            action='tokenbalance',
            address=address,
            contractaddress=contract_address,
            tag=check_tag(tag),
        )

    async def total_supply_by_blockno(self, contract_address: str, blockno: int) -> str:
        """Get Historical ERC20-Token TotalSupply by ContractAddress & BlockNo"""
        return await self._get(
            module='stats',
            action='tokensupplyhistory',
            contractaddress=contract_address,
            blockno=blockno,
        )

    async def account_balance_by_blockno(
        self, address: str, contract_address: str, blockno: int
    ) -> str:
        """Get Historical ERC20-Token Account Balance for TokenContractAddress by BlockNo"""
        return await self._get(
            module='account',
            action='tokenbalancehistory',
            address=address,
            contractaddress=contract_address,
            blockno=blockno,
        )

    async def token_holder_list(
        self,
        contract_address: str,
        page: int = None,
        offset: int = None,
    ) -> List[Dict]:
        """Get Token Holder List by Contract Address"""
        return await self._get(
            action='tokenholderlist', contractaddress=contract_address, page=page, offset=offset
        )

    async def token_info(
        self,
        contract_address: str = None,
    ) -> List[Dict]:
        """Get Token Info by ContractAddress"""
        return await self._get(
            action='tokeninfo',
            contractaddress=contract_address,
        )

    async def token_holding_erc20(
        self,
        address: str,
        page: int = None,
        offset: int = None,
    ) -> List[Dict]:
        """Get Address ERC20 Token Holding"""
        return await self._get(
            module='account',
            action='addresstokenbalance',
            address=address,
            page=page,
            offset=offset,
        )

    async def token_holding_erc721(
        self,
        address: str,
        page: int = None,
        offset: int = None,
    ) -> List[Dict]:
        """Get Address ERC721 Token Holding"""
        return await self._get(
            module='account',
            action='addresstokennftbalance',
            address=address,
            page=page,
            offset=offset,
        )

    async def token_inventory(
        self,
        address: str,
        contract_address: str,
        page: int = None,
        offset: int = None,
    ) -> List[Dict]:
        """Get Address ERC721 Token Inventory By Contract Address"""
        return await self._get(
            module='account',
            action='addresstokennftinventory',
            address=address,
            contractaddress=contract_address,
            page=page,
            offset=offset,
        )
