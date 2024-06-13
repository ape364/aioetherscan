import logging


class Limit:
    def __init__(self, limit: int, blocks_range_divider: int) -> None:
        self._initial_limit = limit
        self._limit = self._initial_limit

        self._blocks_range_divider = blocks_range_divider

        self._logger = logging.getLogger(__name__)

    def get(self) -> int:
        self._logger.debug(f'Limit initial/current: {self._initial_limit:,}/{self._limit:,}')
        return self._limit

    def reduce(self) -> None:
        new_limit = self._limit // self._blocks_range_divider
        if new_limit == 0:
            raise Exception('Limit is 0')
        self._logger.debug(f'Reducing limit from {self._limit:,} to {new_limit:,}')
        self._limit = new_limit

    def restore(self) -> None:
        self._limit = self._initial_limit


class BlocksRange:
    def __init__(
        self, start_block: int, end_block: int, blocks_limit: int, blocks_limit_divider: int
    ) -> None:
        self.start_block = start_block
        self.end_block = end_block

        self._current_block = start_block

        self.limit = Limit(blocks_limit, blocks_limit_divider)

        self._logger = logging.getLogger(__name__)

        self._logger.debug(
            f'Initial blocks range: {self.start_block:,}..{self.end_block:,} ({self.size:,})'
        )

    @property
    def current_block(self) -> int:
        return self._current_block

    @current_block.setter
    def current_block(self, value: int) -> None:
        block = min(value, self.end_block)
        self._logger.info(f'Current block is changed from {self._current_block:,} to {block:,}')
        self._current_block = block

    def get_blocks_range(self) -> range:
        start_block = self._current_block
        end_block = min(self.end_block, self._current_block + self.limit.get() - 1)
        rng = range(start_block, end_block)
        self._logger.debug(
            f'Returning blocks range: {rng.start:,}..{rng.stop:,} ({rng.stop - rng.start + 1:,})'
        )
        return rng

    @property
    def blocks_done(self) -> int:
        return self._current_block - self.start_block

    @property
    def blocks_left(self) -> int:
        return self.end_block - self.current_block

    @property
    def size(self) -> int:
        return self.end_block - self.start_block + 1
