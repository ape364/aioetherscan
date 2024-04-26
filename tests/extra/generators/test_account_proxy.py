# # TODO: write tests
# from unittest.mock import patch, call, AsyncMock, MagicMock, Mock
#
# import pytest
# import pytest_asyncio
#
# import aioetherscan.modules.extra
# from aioetherscan import Client
# from aioetherscan.exceptions import EtherscanClientApiError
#
#
# @pytest_asyncio.fixture
# async def generators():
#     c = Client('TestApiKey')
#     yield c.extra.generators
#     await c.close()
#
#
# @pytest.mark.asyncio
# async def test_token_transfers(generators):
#     # get_parser_params_mock = Mock()
#     # generators._get_parser_params = get_parser_params_mock
#
#     parse_by_blocks_mock = MagicMock()
#     parse_by_blocks_mock.__aiter__.return_value = range(3)
#     generators._parse_by_blocks = parse_by_blocks_mock
#
#     params = dict(
#         contract_address='contract_addr',
#         address='addr',
#         start_block=1,
#         end_block=2,
#         blocks_limit=10,
#         blocks_limit_divider=20
#     )
#     with patch(
#             'aioetherscan.modules.extra.GeneratorUtils._get_parser_params', new=AsyncMock()
#     ) as get_parser_params_mock:
#         async for t in generators.token_transfers(**params):
#             pass
#             # get_parser_params_mock.assert_not_called()
#
# # def test_generate_intervals(utils):
# #     expected = [(1, 3), (4, 6), (7, 9), (10, 10)]
# #     for i, j in utils._generate_intervals(1, 10, 3):
# #         assert (i, j) == expected.pop(0)
# #
# #     expected = [(1, 2), (3, 4), (5, 6)]
# #     for i, j in utils._generate_intervals(1, 6, 2):
# #         assert (i, j) == expected.pop(0)
# #
# #     for _, _ in utils._generate_intervals(10, 0, 3):
# #         assert True is False  # not called
# #
# #
# # @pytest.mark.asyncio
# # async def test_parse_by_pages(utils):
# #     with patch('aioetherscan.modules.account.Account.token_transfers', new=AsyncMock()) as transfers_mock:
# #         transfers_mock.side_effect = EtherscanClientApiError('No transactions found', None)
# #         async for _ in utils._parse_by_pages(
# #                 100,
# #                 200,
# #                 5,
# #                 address='address',
# #                 contract_address='contract_address',
# #         ):
# #             break
# #         transfers_mock.assert_called_once_with(
# #             address='address',
# #             contract_address='contract_address',
# #             start_block=100,
# #             end_block=200,
# #             page=1,
# #             offset=5
# #         )
# #
# #
# # @pytest.mark.asyncio
# # async def test_parse_by_pages_exception(utils):
# #     with patch('aioetherscan.modules.account.Account.token_transfers', new=AsyncMock()) as transfers_mock:
# #         transfers_mock.side_effect = EtherscanClientApiError('other msg', None)
# #         try:
# #             async for _ in utils._parse_by_pages(
# #                     100,
# #                     200,
# #                     5,
# #                     address='address',
# #                     contract_address='contract_address',
# #             ):
# #                 break
# #         except EtherscanClientApiError as e:
# #             assert e.message == 'other msg'
# #
# #
# # @pytest.mark.asyncio
# # async def test_parse_by_pages_result(utils):
# #     def token_transfers_side_effect_generator():
# #         yield [1]
# #         yield [2]
# #         raise EtherscanClientApiError('No transactions found', None)
# #
# #     gen = token_transfers_side_effect_generator()
# #
# #     # noinspection PyUnusedLocal
# #     def token_transfers_side_effect(**kwargs):
# #         for x in gen:
# #             return x
# #
# #     with patch('aioetherscan.modules.account.Account.token_transfers', new=AsyncMock()) as transfers_mock:
# #         transfers_mock.side_effect = token_transfers_side_effect
# #
# #         i = 0
# #         res = []
# #         async for transfer in utils._parse_by_pages(
# #                 100,
# #                 200,
# #                 5,
# #                 address='address',
# #                 contract_address='contract_address',
# #         ):
# #             i += 1
# #             if i > 2:
# #                 break
# #             res.append(transfer)
# #         transfers_mock.assert_has_calls(
# #             [
# #                 call(
# #                     address='address',
# #                     contract_address='contract_address',
# #                     start_block=100,
# #                     end_block=200,
# #                     page=1,
# #                     offset=5
# #                 ),
# #                 call(
# #                     address='address',
# #                     contract_address='contract_address',
# #                     start_block=100,
# #                     end_block=200,
# #                     page=2,
# #                     offset=5
# #                 ),
# #                 call(
# #                     address='address',
# #                     contract_address='contract_address',
# #                     start_block=100,
# #                     end_block=200,
# #                     page=3,
# #                     offset=5
# #                 ),
# #             ]
# #         )
# #         assert res == [1, 2]
# #
# #
# # @pytest.mark.asyncio
# # async def test_token_transfers(utils):
# #     with patch(
# #             'aioetherscan.modules.extra.utils.Utils.token_transfers_generator',
# #             new=MagicMock()
# #     ) as transfers_gen_mock:
# #         await utils.token_transfers(
# #             contract_address='contract_address'
# #         )
# #         transfers_gen_mock.assert_called_once_with(
# #             contract_address='contract_address',
# #             address=None,
# #             be_polite=True,
# #             block_limit=50,
# #             offset=3,
# #             start_block=0,
# #             end_block=None,
# #         )
# #
# #
# # @pytest.mark.asyncio
# # async def test_token_transfers_generator(utils):
# #     with patch('aioetherscan.modules.extra.utils.Utils._parse_by_pages', new=MagicMock()) as parse_mock:
# #         with patch('aioetherscan.modules.proxy.Proxy.block_number', new=AsyncMock()) as proxy_mock:
# #             proxy_mock.return_value = '0x14'
# #
# #             async for _ in utils.token_transfers_generator(address='addr'):
# #                 break
# #
# #             parse_mock.assert_called_once_with(
# #                 address='addr',
# #                 contract_address=None,
# #                 start_block=0,
# #                 end_block=20,
# #                 offset=3,
# #             )
# #
# #     with patch('aioetherscan.modules.extra.utils.Utils._parse_by_pages', new=MagicMock()) as parse_mock:
# #         async for _ in utils.token_transfers_generator(
# #                 contract_address='contract_address',
# #                 end_block=20,
# #         ):
# #             break
# #
# #         parse_mock.assert_called_once_with(
# #             address=None,
# #             contract_address='contract_address',
# #             start_block=0,
# #             end_block=20,
# #             offset=3,
# #         )
# #
# #
# # @pytest.mark.asyncio
# # async def test_one_of_addresses_is_supplied(utils):
# #     exception_message_re = r'At least one of address or contract_address must be specified.'
# #     with pytest.raises(ValueError, match=exception_message_re):
# #         async for _ in utils.token_transfers_generator(end_block=1):
# #             break
