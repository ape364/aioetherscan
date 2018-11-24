from typing import Union, Dict

from aioetherscan.common import check_hex, check_tag
from aioetherscan.modules.base import BaseModule


class Proxy(BaseModule):
    """Geth/Parity Proxy APIs

    https://etherscan.io/apis#proxy
    https://github.com/ethereum/wiki/wiki/JSON-RPC
    """

    @property
    def _module(self) -> str:
        return 'proxy'

    async def block_number(self) -> str:
        """Returns the number of most recent block."""
        return await self._get(action='eth_blockNumber')

    async def block_by_number(self, full: bool, tag: Union[int, str] = 'latest') -> Dict:
        """Returns information about a block by block number."""
        return await self._get(
            action='eth_getBlockByNumber',
            boolean=full,
            tag=check_tag(tag),
        )

    async def uncle_block_by_number_and_index(self, index: Union[int, str], tag: Union[int, str] = 'latest') -> Dict:
        """Returns information about a uncle by block number."""
        return await self._get(
            action='eth_getUncleByBlockNumberAndIndex',
            index=check_hex(index),
            tag=check_tag(tag),
        )

    async def block_tx_count_by_number(self, tag: Union[int, str] = 'latest') -> str:
        """Returns the number of transactions in a block from a block matching the given block number."""
        return await self._get(
            action='eth_getBlockTransactionCountByNumber',
            tag=check_tag(tag),
        )

    async def tx_by_hash(self, txhash: Union[int, str]) -> Dict:
        """Returns the information about a transaction requested by transaction hash."""
        return await self._get(
            action='eth_getTransactionByHash',
            txhash=check_hex(txhash),
        )

    async def tx_by_number_and_index(self, index: Union[int, str], tag: Union[int, str] = 'latest') -> Dict:
        """Returns information about a transaction by block number and transaction index position."""
        return await self._get(
            action='eth_getTransactionByBlockNumberAndIndex',
            index=check_hex(index),
            tag=check_tag(tag),
        )

    async def tx_count(self, address: str, tag: Union[int, str] = 'latest') -> str:
        """Returns the number of transactions sent from an address."""
        return await self._get(
            action='eth_getTransactionCount',
            address=address,
            tag=check_tag(tag),
        )

    async def send_raw_tx(self, raw_hex: str) -> Dict:
        """Creates new message call transaction or a contract creation for signed transactions."""
        return await self._post(
            module='proxy',
            action='eth_sendRawTransaction',
            hex=raw_hex
        )

    async def tx_receipt(self, txhash: str) -> Dict:
        """Returns the receipt of a transaction by transaction hash."""
        return await self._get(
            action='eth_getTransactionReceipt',
            txhash=check_hex(txhash),
        )

    async def call(self, to: str, data: str, tag: Union[int, str] = 'latest') -> str:
        """Executes a new message call immediately without creating a transaction on the block chain."""
        return await self._get(
            action='eth_call',
            to=check_hex(to),
            data=check_hex(data),
            tag=check_tag(tag),
        )

    async def code(self, address: str, tag: Union[int, str] = 'latest') -> str:
        """Returns code at a given address."""
        return await self._get(
            action='eth_getCode',
            address=address,
            tag=check_tag(tag),
        )

    async def storage_at(self, address: str, position: str, tag: Union[int, str] = 'latest') -> str:
        """Returns the value from a storage position at a given address."""
        return await self._get(
            action='eth_getStorageAt',
            address=address,
            position=position,
            tag=check_tag(tag),
        )

    async def gas_price(self) -> str:
        """Returns the current price per gas in wei."""
        return await self._get(action='eth_gasPrice', )

    async def estimate_gas(self, to: str, value: str, gas_price: str, gas: str) -> str:
        """Makes a call or transaction, which won't be added to the blockchain and returns the used gas.

        Can be used for estimating the used gas.
        """
        return await self._get(
            action='eth_estimateGas',
            to=check_hex(to),
            value=value,
            gasPrice=gas_price,
            gas=gas,
        )
