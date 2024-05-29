from unittest.mock import Mock, patch, MagicMock, AsyncMock

import pytest

from aioetherscan.exceptions import EtherscanClientApiError
from aioetherscan.modules.extra.generators.blocks_parser import BlocksParser
from aioetherscan.modules.extra.generators.generator_utils import GeneratorUtils


@pytest.fixture
def generator_utils():
    return GeneratorUtils(Mock())


async def parse_mock(*args, **kwargs):
    yield None


def test_transfers() -> list[dict[str, str]]:
    return [{'result': 'transfer1'}, {'result': 'transfer2'}]


async def transfers_mock(*args, **kwargs):
    for t in test_transfers():
        yield t


def test_init_with_default_values():
    client = Mock()
    utils = GeneratorUtils(client)

    assert utils._client == client


def test_get_blocks_parser(generator_utils):
    blocks_parser = generator_utils._get_blocks_parser(
        api_method=None,
        request_params={'param': 'value'},
        start_block=100,
        end_block=200,
        blocks_limit=1000,
        blocks_limit_divider=2,
    )
    assert isinstance(blocks_parser, BlocksParser)


@pytest.mark.asyncio
async def test_token_transfers(generator_utils):
    params_return_value = {'param': 'value'}
    generator_utils._get_parser_params = Mock(return_value=params_return_value)

    with patch(
        'aioetherscan.modules.extra.generators.generator_utils.GeneratorUtils._parse_by_blocks',
        new=MagicMock(side_effect=parse_mock),
    ) as mock:
        async for _ in generator_utils.token_transfers(
            contract_address='c1', address='a1', start_block=0, end_block=20
        ):
            break

        generator_utils._get_parser_params.assert_called_once_with(
            generator_utils._client.account.token_transfers,
            {
                'self': generator_utils,
                'contract_address': 'c1',
                'address': 'a1',
                'start_block': 0,
                'end_block': 20,
                'blocks_limit': 2048,
                'blocks_limit_divider': 2,
            },
        )

        mock.assert_called_once_with(param='value')


@pytest.mark.asyncio
async def test_normal_txs(generator_utils):
    params_return_value = {'param': 'value'}
    generator_utils._get_parser_params = Mock(return_value=params_return_value)

    with patch(
        'aioetherscan.modules.extra.generators.generator_utils.GeneratorUtils._parse_by_blocks',
        new=MagicMock(side_effect=parse_mock),
    ) as mock:
        async for _ in generator_utils.normal_txs(address='a1', start_block=0, end_block=20):
            break

        generator_utils._get_parser_params.assert_called_once_with(
            generator_utils._client.account.normal_txs,
            {
                'self': generator_utils,
                'address': 'a1',
                'start_block': 0,
                'end_block': 20,
                'blocks_limit': 2048,
                'blocks_limit_divider': 2,
            },
        )

        mock.assert_called_once_with(param='value')


@pytest.mark.asyncio
async def test_internal_txs(generator_utils):
    params_return_value = {'param': 'value'}
    generator_utils._get_parser_params = Mock(return_value=params_return_value)

    with patch(
        'aioetherscan.modules.extra.generators.generator_utils.GeneratorUtils._parse_by_blocks',
        new=MagicMock(side_effect=parse_mock),
    ) as mock:
        async for _ in generator_utils.internal_txs(
            address='a1', start_block=0, end_block=20, txhash='0x123'
        ):
            break

        generator_utils._get_parser_params.assert_called_once_with(
            generator_utils._client.account.internal_txs,
            {
                'self': generator_utils,
                'address': 'a1',
                'txhash': '0x123',
                'start_block': 0,
                'end_block': 20,
                'blocks_limit': 2048,
                'blocks_limit_divider': 2,
            },
        )

        mock.assert_called_once_with(param='value')


@pytest.mark.asyncio
async def test_mined_blocks(generator_utils):
    params_return_value = {'param': 'value'}
    generator_utils._get_parser_params = Mock(return_value=params_return_value)

    with patch(
        'aioetherscan.modules.extra.generators.generator_utils.GeneratorUtils._parse_by_pages',
        new=MagicMock(side_effect=parse_mock),
    ) as mock:
        async for _ in generator_utils.mined_blocks(address='a1', blocktype='blocks'):
            break

        generator_utils._get_parser_params.assert_called_once_with(
            generator_utils._client.account.mined_blocks,
            {'self': generator_utils, 'address': 'a1', 'blocktype': 'blocks', 'offset': 10000},
        )

        mock.assert_called_once_with(param='value')


@pytest.mark.asyncio
async def test_parse_by_blocks(generator_utils):
    blocks_parser_mock = Mock()
    blocks_parser_mock.return_value.txs_generator = MagicMock(side_effect=transfers_mock)
    generator_utils._get_blocks_parser = blocks_parser_mock

    transfers = []
    async for transfer in generator_utils._parse_by_blocks(
        api_method=None,
        request_params={'param': 'value'},
        start_block=100,
        end_block=200,
        blocks_limit=1000,
        blocks_limit_divider=2,
    ):
        transfers.append(transfer)
    assert transfers == test_transfers()

    blocks_parser_mock.assert_called_once_with(None, {'param': 'value'}, 100, 200, 1000, 2)


async def test_parse_by_blocks_end_block_is_none(generator_utils):
    blocks_parser_mock = Mock()
    blocks_parser_mock.return_value.txs_generator = MagicMock(side_effect=transfers_mock)
    generator_utils._get_blocks_parser = blocks_parser_mock

    current_block = 200
    get_current_block_mock = AsyncMock(return_value=current_block)
    generator_utils._get_current_block = get_current_block_mock

    transfers = []
    async for transfer in generator_utils._parse_by_blocks(
        api_method=None,
        request_params={'param': 'value'},
        start_block=100,
        end_block=None,
        blocks_limit=1000,
        blocks_limit_divider=2,
    ):
        transfers.append(transfer)
    assert transfers == test_transfers()

    get_current_block_mock.assert_awaited_once()
    blocks_parser_mock.assert_called_once_with(
        None, {'param': 'value'}, 100, current_block, 1000, 2
    )


async def test_parse_by_pages_ok(generator_utils):
    api_method = AsyncMock(return_value=['row1', 'row2'])
    params = {'param': 'value'}

    result = []
    async for row in generator_utils._parse_by_pages(api_method, params):
        result.append(row)

        if len(row) > 1:
            api_method.side_effect = EtherscanClientApiError('No transactions found', 'result')

    assert result == api_method.return_value


async def test_parse_by_pages_error(generator_utils):
    api_method = AsyncMock(side_effect=EtherscanClientApiError('test error'))
    params = {'param': 'value'}

    with pytest.raises(EtherscanClientApiError) as e:
        async for _ in generator_utils._parse_by_pages(api_method, params):
            break

    assert e.value.args[0] == 'test error'


async def test_get_current_block(generator_utils):
    generator_utils._client = Mock()
    generator_utils._client.proxy.block_number = AsyncMock(return_value='0x2d0')

    result = await generator_utils._get_current_block()

    generator_utils._client.proxy.block_number.assert_awaited_once()
    assert isinstance(result, int)
    assert result == int('0x2d0', 16)


async def test_get_current_block_error(generator_utils):
    generator_utils._client = Mock()
    generator_utils._client.proxy.block_number = AsyncMock(
        side_effect=EtherscanClientApiError('message', 'code')
    )

    with pytest.raises(EtherscanClientApiError) as e:
        await generator_utils._get_current_block()

    generator_utils._client.proxy.block_number.assert_awaited_once()

    assert e.value.message == 'message'
    assert e.value.result == 'code'


@pytest.mark.parametrize(
    'params, excluded, expected',
    [
        ({'a': 1, 'b': 2, 'c': 3}, ('a', 'b'), {'c': 3}),
        ({'a': 1, 'b': 2, 'c': 3}, ('b', 'c'), {'a': 1}),
        ({'a': 1, 'b': 2, 'c': 3}, ('a', 'c'), {'b': 2}),
        ({'a': 1, 'b': 2, 'c': 3}, ('a', 'b', 'c'), {}),
        ({'a': 1, 'b': 2, 'c': 3}, ('d', 'e'), {'a': 1, 'b': 2, 'c': 3}),
    ],
)
def test_without_keys(generator_utils, params, excluded, expected):
    assert generator_utils._without_keys(params, excluded) == expected


def test_get_request_params(generator_utils):
    api_method = object()

    generator_utils._without_keys = Mock(return_value={'param1': 'value1', 'param2': 'value2'})

    with patch('inspect.getfullargspec') as getfullargspec_mock:
        getfullargspec_mock.return_value.args = ['self', 'param1', 'param3']

        result = generator_utils._get_request_params(
            api_method, {'param1': 'value1', 'param2': 'value2'}
        )

        getfullargspec_mock.assert_called_once_with(api_method)
        generator_utils._without_keys.assert_called_once_with(
            {'param1': 'value1'}, ('self', 'start_block', 'end_block')
        )
        assert result == generator_utils._without_keys.return_value


def test_get_parser_params(generator_utils):
    api_method = object()
    params = {'param1': 'value1', 'param2': 'value2', 'param3': 'value3'}

    generator_utils._get_request_params = Mock(return_value={'param1': 'value1'})
    result = generator_utils._get_parser_params(api_method, params)

    generator_utils._get_request_params.assert_called_once_with(api_method, params)

    assert result == dict(
        api_method=api_method,
        request_params=generator_utils._get_request_params.return_value,
        **{'param2': 'value2', 'param3': 'value3'},
    )
