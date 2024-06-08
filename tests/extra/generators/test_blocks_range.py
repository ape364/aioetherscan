from logging import Logger

import pytest

from aioetherscan.modules.extra.generators.blocks_range import Limit, BlocksRange

INITIAL_LIMIT = 2 ** 4
BLOCKS_RANGE_DIVIDER = 2

START_BLOCK = 1000
END_BLOCK = 5000


@pytest.fixture
def limit() -> Limit:
    yield Limit(INITIAL_LIMIT, BLOCKS_RANGE_DIVIDER)


@pytest.fixture
def br(limit: Limit) -> BlocksRange:
    yield BlocksRange(
        START_BLOCK,
        END_BLOCK,
        INITIAL_LIMIT,
        BLOCKS_RANGE_DIVIDER,
    )


# ############################### limit ################################


def test_limit_init(limit: Limit):
    assert limit._limit == INITIAL_LIMIT
    assert limit._initial_limit == INITIAL_LIMIT
    assert limit._blocks_range_divider == BLOCKS_RANGE_DIVIDER

    assert isinstance(limit._logger, Logger)


def test_limit_reduce(limit: Limit):
    limit.reduce()
    assert limit.get() == INITIAL_LIMIT // BLOCKS_RANGE_DIVIDER
    assert limit._initial_limit == INITIAL_LIMIT


def test_limit_reduce_raise(limit: Limit):
    while limit.get() != 1:
        limit.reduce()

    with pytest.raises(Exception) as e:
        limit.reduce()
    assert e.value.args[0] == 'Limit is 0'


def test_limit_restore(limit: Limit):
    limit.reduce()
    limit.restore()

    assert limit.get() == INITIAL_LIMIT


def test_limit_get(limit: Limit):
    assert limit.get() == INITIAL_LIMIT


# ############################### blocks range ################################

def test_br_init(br: BlocksRange):
    assert br.start_block == START_BLOCK
    assert br.end_block == END_BLOCK
    assert br.current_block == START_BLOCK

    assert isinstance(br.limit, Limit)
    assert isinstance(br._logger, Logger)
