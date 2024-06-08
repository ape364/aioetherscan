import inspect
import sys
from itertools import count
from typing import Callable, Any, Optional, TYPE_CHECKING, AsyncIterator

from aioetherscan.exceptions import EtherscanClientApiError
from aioetherscan.modules.extra.generators.blocks_parser import BlocksParser, Transfer

if TYPE_CHECKING:  # pragma: no cover
    from aioetherscan import Client


class GeneratorUtils:
    _DEFAULT_START_BLOCK: int = 0
    _DEFAULT_END_BLOCK: int = sys.maxsize
    _DEFAULT_BLOCKS_LIMIT: int = 2048
    _DEFAULT_BLOCKS_LIMIT_DIVIDER: int = 2

    def __init__(self, client: 'Client') -> None:
        self._client = client

    async def token_transfers(
        self,
        contract_address: str = None,
        address: str = None,
        start_block: int = _DEFAULT_START_BLOCK,
        end_block: int = _DEFAULT_END_BLOCK,
        blocks_limit: int = _DEFAULT_BLOCKS_LIMIT,
        blocks_limit_divider: int = _DEFAULT_BLOCKS_LIMIT_DIVIDER,
    ) -> AsyncIterator[Transfer]:
        parser_params = self._get_parser_params(self._client.account.token_transfers, locals())
        async for transfer in self._parse_by_blocks(**parser_params):
            yield transfer

    async def normal_txs(
        self,
        address: str,
        start_block: int = _DEFAULT_START_BLOCK,
        end_block: int = _DEFAULT_END_BLOCK,
        blocks_limit: int = _DEFAULT_BLOCKS_LIMIT,
        blocks_limit_divider: int = _DEFAULT_BLOCKS_LIMIT_DIVIDER,
    ) -> AsyncIterator[Transfer]:
        parser_params = self._get_parser_params(self._client.account.normal_txs, locals())
        async for transfer in self._parse_by_blocks(**parser_params):
            yield transfer

    async def internal_txs(
        self,
        address: str,
        start_block: int = _DEFAULT_START_BLOCK,
        end_block: int = _DEFAULT_END_BLOCK,
        blocks_limit: int = _DEFAULT_BLOCKS_LIMIT,
        blocks_limit_divider: int = _DEFAULT_BLOCKS_LIMIT_DIVIDER,
        txhash: Optional[str] = None,
    ) -> AsyncIterator[Transfer]:
        parser_params = self._get_parser_params(self._client.account.internal_txs, locals())
        async for transfer in self._parse_by_blocks(**parser_params):
            yield transfer

    async def mined_blocks(
        self, address: str, blocktype: str, offset: int = 10_000
    ) -> AsyncIterator[Transfer]:
        parser_params = self._get_parser_params(self._client.account.mined_blocks, locals())
        async for transfer in self._parse_by_pages(**parser_params):
            yield transfer

    async def _parse_by_blocks(
        self,
        api_method: Callable,
        request_params: dict[str, Any],
        start_block: int,
        end_block: int,
        blocks_limit: int,
        blocks_limit_divider: int,
    ) -> AsyncIterator[Transfer]:
        blocks_parser = self._get_blocks_parser(
            api_method, request_params, start_block, end_block, blocks_limit, blocks_limit_divider
        )
        async for tx in blocks_parser.txs_generator():
            yield tx

    @staticmethod
    async def _parse_by_pages(
        api_method: Callable, request_params: dict[str, Any]
    ) -> AsyncIterator[Transfer]:
        page = count(1)
        while True:
            request_params['page'] = next(page)
            try:
                result = await api_method(**request_params)
            except EtherscanClientApiError as e:
                if e.message == 'No transactions found':
                    return
                raise
            else:
                for row in result:
                    yield row

    @staticmethod
    def _without_keys(params: dict, excluded_keys: tuple[str, ...] = ('self',)) -> dict:
        return {k: v for k, v in params.items() if k not in excluded_keys}

    def _get_parser_params(self, api_method: Callable, params: dict[str, Any]) -> dict[str, Any]:
        request_params = self._get_request_params(api_method, params)
        return dict(
            api_method=api_method,
            request_params=request_params,
            **{k: v for k, v in params.items() if k not in request_params},
        )

    def _get_request_params(self, api_method: Callable, params: dict[str, Any]) -> dict[str, Any]:
        api_method_params = inspect.getfullargspec(api_method).args
        return self._without_keys(
            {k: v for k, v in params.items() if k in api_method_params},
            ('self', 'start_block', 'end_block'),
        )

    @staticmethod
    def _get_blocks_parser(
        api_method: Callable,
        request_params: dict[str, Any],
        start_block: int,
        end_block: int,
        blocks_limit: int,
        blocks_limit_divider: int,
    ) -> BlocksParser:
        return BlocksParser(
            api_method, request_params, start_block, end_block, blocks_limit, blocks_limit_divider
        )
