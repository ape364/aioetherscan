import logging
from unittest.mock import AsyncMock

import pytest

from aioetherscan.exceptions import EtherscanClientApiError
from aioetherscan.modules.extra.generators.blocks_parser import BlocksParser
from aioetherscan.modules.extra.generators.blocks_range import BlocksRange


@pytest.fixture()
async def api_method():
    return AsyncMock()


@pytest.fixture
def request_params():
    return {'param1': 'value1', 'param2': 'value2'}


@pytest.fixture
def start_block():
    return 100


@pytest.fixture
def end_block():
    return 200


@pytest.fixture
def blocks_limit():
    return 10


@pytest.fixture
def blocks_limit_divider():
    return 2


@pytest.fixture
def blocks_parser(
    api_method, request_params, start_block, end_block, blocks_limit, blocks_limit_divider
):
    return BlocksParser(
        api_method, request_params, start_block, end_block, blocks_limit, blocks_limit_divider
    )


def test_blocks_parser_init(
    api_method, request_params, start_block, end_block, blocks_limit, blocks_limit_divider
):
    parser = BlocksParser(
        api_method, request_params, start_block, end_block, blocks_limit, blocks_limit_divider
    )

    assert parser._api_method == api_method
    assert parser._request_params == request_params

    assert isinstance(parser._blocks_range, BlocksRange)
    assert parser._blocks_range.start_block == start_block
    assert parser._blocks_range.end_block == end_block

    assert isinstance(parser._logger, logging.Logger)

    assert parser._total_txs == 0


def test_make_request_params(blocks_parser):
    blocks_range = range(100, 200)
    params = blocks_parser._make_request_params(blocks_range)
    assert params == {
        'start_block': 100,
        'end_block': 200,
        'page': 1,
        'offset': 10_000,
        **blocks_parser._request_params,
    }


async def test_fetch_blocks_range_success(blocks_parser, api_method):
    api_method.return_value = [{'blockNumber': 100}]
    blocks_range = range(100, 101)
    max_block, transfers = await blocks_parser._fetch_blocks_range(blocks_range)
    assert max_block == 100
    assert transfers == [{'blockNumber': 100}]


async def test_fetch_blocks_range_empty_response(blocks_parser, api_method):
    max_block_default = 100
    api_method.return_value = [{'blockNumber': max_block_default}] * BlocksParser._OFFSET
    blocks_range = range(100, 101)
    max_block, transfers = await blocks_parser._fetch_blocks_range(blocks_range)

    assert max_block == max_block_default - 1
    assert {'blockNumber': max_block_default} not in transfers


async def test_fetch_blocks_range_api_error(blocks_parser, api_method):
    api_method.side_effect = EtherscanClientApiError('Test exception', 'result')
    blocks_range = range(100, 101)
    with pytest.raises(EtherscanClientApiError):
        await blocks_parser._fetch_blocks_range(blocks_range)


async def test_fetch_blocks_range_no_txs(blocks_parser, api_method):
    api_method.side_effect = EtherscanClientApiError('No transactions found', 'result')

    blocks_range = range(100, 101)
    max_block, transfers = await blocks_parser._fetch_blocks_range(blocks_range)

    assert max_block == blocks_range.stop
    assert transfers == []


async def test_txs_generator_success(blocks_parser, api_method):
    api_method.return_value = [{'blockNumber': 200, 'transfers': [{'value': 100}]}]
    transfers = []
    async for transfer in blocks_parser.txs_generator():
        transfers.append(transfer)
    assert transfers == [{'blockNumber': 200, 'transfers': [{'value': 100}]}]


async def test_txs_generator_empty_response(blocks_parser, api_method):
    api_method.return_value = []
    transfers = []
    async for transfer in blocks_parser.txs_generator():
        transfers.append(transfer)
    assert transfers == []
