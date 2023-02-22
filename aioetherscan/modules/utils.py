from itertools import count, tee
from typing import (
    TYPE_CHECKING, Any, TypeVar, Union, Optional, Callable,
    Tuple, List, Iterable, Iterator, AsyncIterator, Awaitable,
)
from urllib.parse import urljoin, urlencode

from asyncio_throttle import Throttler

from aioetherscan.exceptions import EtherscanClientApiError
if TYPE_CHECKING:
    from ..client import Client

T = TypeVar("T")
Ordered = Union[T, List[T], Tuple[T, ...]]


class BaseProxy:
    """Helper methods to iterate through pagination."""

    def __init__(self, client: "Client"):
        self._client = client
        # Defaulting to free API key rate limit
        self._throttler = Throttler(rate_limit=5, period=1.0)

    @property
    def throttler(self) -> Throttler:
        return self._throttler

    @throttler.setter
    def throttler(self, value: Throttler):
        if isinstance(value, Throttler):
            self._throttler = value

    @staticmethod
    def generate_intervals(from_number: int, to_number: int, count_: int) -> Iterator[Tuple[int, int]]:
        for i in range(from_number, to_number + 1, count_):
            yield (i, min(i + count_ - 1, to_number))

    def proxy(self, func: Callable[..., Awaitable[Iterable[T]]]):

        async def wrapper(*args, **kwargs) -> AsyncIterator[T]:

            async with self.throttler:
                result = await func(*args, **kwargs)
            for v in result:
                yield v

        return wrapper

    def parametrize(
        self,
        argnames: Ordered[str],
        argvalues: Iterable[Ordered[Any]],
        stop_if_empty: bool = True,
    ):
        if isinstance(argnames, str):
            argnames = argnames.split(',')

        if len(argnames) == 1:
            argvalues = ((v,) for v in argvalues)

        def inner(func: Callable[..., AsyncIterator[T]]):

            async def wrapper(*args, **kwargs) -> AsyncIterator[T]:
                nonlocal argvalues
                argvalues, helper = tee(argvalues)
                for values in helper:
                    kwargs.update(zip(argnames, values))
                    try:
                        async for v in func(*args, **kwargs):
                            yield v
                    except EtherscanClientApiError as exc:
                        if exc.message != 'No transactions found':
                            raise
                        if stop_if_empty:
                            return
                        else:
                            continue

            return wrapper

        return inner

    async def parse_by_pages(
        self,
        func: Callable[..., AsyncIterator[T]],
        *args,
        **kwargs,
    ) -> AsyncIterator[T]:
        @self.parametrize("page", count(1))
        async def _proxy(*arg, **kwarg):
            async for v in self.proxy(func)(*arg, **kwarg):
                yield v

        async for v in _proxy(*args, **kwargs):
            yield v

    async def parse_by_blocks(
        self,
        func: Callable[..., AsyncIterator[T]],
        *args,
        start_block: int = 0,
        end_block: int = None,
        block_limit: int = 10_000,
        **kwargs,
    ) -> AsyncIterator[T]:

        if end_block is None:
            end_block = int(await self._client.proxy.block_number(), 16)

        @self.parametrize(
            "start_block,end_block",
            self.generate_intervals(start_block, end_block, block_limit),
            stop_if_empty=False,
        )
        async def _proxy(*arg, **kwarg):
            async for v in self.parse_by_pages(func, *arg, **kwarg):
                yield v

        async for v in _proxy(*args, **kwargs):
            yield v


class AccountProxy(BaseProxy):
    async def normal_txs_generator(self, *args, **kwargs):
        async for v in self.parse_by_blocks(self._client.account.normal_txs, *args, **kwargs):
            yield v

    async def internal_txs_generator(self, *args, **kwargs):
        async for v in self.parse_by_blocks(self._client.account.internal_txs, *args, **kwargs):
            yield v

    async def token_transfers_generator(self, *args, **kwargs):
        async for v in self.parse_by_blocks(self._client.account.token_transfers, *args, **kwargs):
            yield v

    async def mined_blocks_generator(self, *args, **kwargs):
        async for v in self.parse_by_pages(self._client.account.mined_blocks, *args, **kwargs):
            yield v


class Utils:
    """Helper methods which use the combination of documented APIs."""

    def __init__(self, client: "Client", base_url: str):
        self._client = client
        self._BASE_URL = base_url
        self.account_proxy = AccountProxy(client)

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
