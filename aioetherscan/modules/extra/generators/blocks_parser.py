import logging
from typing import AsyncIterator, TypeAlias, Any, Iterable
from typing import Callable

from aioetherscan.exceptions import EtherscanClientApiError
from aioetherscan.modules.extra.generators.blocks_range import BlocksRange
from aioetherscan.modules.extra.generators.helpers import get_max_block_number, drop_block

Transfer: TypeAlias = dict[str, Any]


class BlocksParser:
    _OFFSET: int = 10_000

    def __init__(
            self,
            api_method: Callable,
            request_params: dict[str, Any],
            start_block: int,
            end_block: int,
            blocks_limit: int,
            blocks_limit_divider: int
    ) -> None:
        self._api_method = api_method
        self._request_params = request_params

        self._blocks_range = BlocksRange(
            start_block,
            end_block,
            blocks_limit,
            blocks_limit_divider
        )

        self._logger = logging.getLogger(__name__)
        self._total_txs = 0

    async def txs_generator(self) -> AsyncIterator[Transfer]:
        while self._blocks_range.blocks_left:
            try:
                blocks_range = self._blocks_range.get_blocks_range()
                last_seen_block, transfers = await self._fetch_blocks_range(blocks_range)
            except EtherscanClientApiError as e:
                self._logger.error(f'Error: {e}')
                self._blocks_range.limit.reduce()
            else:
                self._blocks_range.current_block = last_seen_block + 1
                self._blocks_range.limit.restore()

                for transfer in transfers:
                    yield transfer

                self._logger.info(
                    f'[{self._blocks_range.blocks_done / self._blocks_range.size:.2%}] '
                    f'Current block {self._blocks_range.current_block:,} '
                    f'({self._blocks_range.blocks_left:,} blocks left)'
                )

    def _make_request_params(self, blocks_range: range) -> Transfer:
        current_params = dict(
            start_block=blocks_range.start,
            end_block=blocks_range.stop,
            page=1,
            offset=self._OFFSET,
        )
        params = self._request_params | current_params
        self._logger.debug(f'Request params: {params}')
        return params

    async def _fetch_blocks_range(self, blocks_range: range) -> tuple[int, Iterable[Transfer]]:
        try:
            request_params = self._make_request_params(blocks_range)
            transfers = await self._api_method(**request_params)
        except EtherscanClientApiError as e:
            if e.message == 'No transactions found':
                return blocks_range.stop, []
            raise
        else:
            transfers_count = len(transfers)
            self._total_txs += transfers_count
            self._logger.debug(f'Got {transfers_count:,} transfers, {self._total_txs:,} total')

            transfers_max_block = get_max_block_number(transfers)

            if transfers_count == self._OFFSET:
                self._logger.debug(
                    f'Probably not all txs have been fetched, dropping txs with the last block {transfers_max_block:,}'
                )
                return transfers_max_block - 1, drop_block(
                    transfers, transfers_max_block
                )
            else:
                self._logger.debug(
                    'All txs have been fetched'
                )
                return transfers_max_block, transfers
