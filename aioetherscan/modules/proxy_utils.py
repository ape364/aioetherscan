from itertools import tee, count
from typing import TypeVar, Union, List, Tuple, Iterator, Callable, Awaitable, Iterable, AsyncIterator, Any

from asyncio_throttle import Throttler

from aioetherscan.exceptions import EtherscanClientApiError

T = TypeVar("T")
Ordered = Union[T, List[T], Tuple[T, ...]]


class BaseProxy:
    """Helper methods to iterate through pagination."""

    def __init__(self, client):
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
            yield i, min(i + count_ - 1, to_number)

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
            func: Callable[..., Awaitable[Iterable[T]]],
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
            func: Callable[..., Awaitable[Iterable[T]]],
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
