from unittest.mock import Mock, patch, MagicMock

import pytest

from aioetherscan.modules.extra.generators.generator_utils import GeneratorUtils


@pytest.fixture
def generator_utils():
    return GeneratorUtils(Mock())


async def parse_mock(*args, **kwargs):
    yield None


def test_init_with_default_values():
    client = Mock()
    utils = GeneratorUtils(client)

    assert utils._client == client


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
