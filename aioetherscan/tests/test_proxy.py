from unittest.mock import patch, Mock, call

import pytest
from asynctest import CoroutineMock

from aioetherscan import Client


@pytest.fixture()
async def proxy():
    c = Client('TestApiKey')
    yield c.proxy
    await c.close()


@pytest.mark.asyncio
async def test_block_number(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.block_number()
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_blockNumber',
            )
        )


@pytest.mark.asyncio
async def test_block_by_number(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.block_by_number(True)
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getBlockByNumber',
                boolean=True,
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
            await proxy.block_by_number(True)
            tag_mock.assert_called_once_with('latest')
            mock.assert_called_once()


@pytest.mark.asyncio
async def test_uncle_block_by_number_and_index(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.uncle_block_by_number_and_index(123)
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getUncleByBlockNumberAndIndex',
                index='0x7b',
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_hex', new=Mock()) as hex_mock:
            with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
                await proxy.uncle_block_by_number_and_index(123)
                hex_mock.assert_called_once_with(123)
                tag_mock.assert_called_once_with('latest')
                mock.assert_called_once()


@pytest.mark.asyncio
async def test_block_tx_count_by_number(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.block_tx_count_by_number()
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getBlockTransactionCountByNumber',
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
            await proxy.block_tx_count_by_number(123)
            tag_mock.assert_called_once_with(123)
            mock.assert_called_once()


@pytest.mark.asyncio
async def test_tx_by_hash(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.tx_by_hash('0x123')
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getTransactionByHash',
                txhash='0x123'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_hex', new=Mock()) as hex_mock:
            await proxy.tx_by_hash(123)
            hex_mock.assert_called_once_with(123)
            mock.assert_called_once()


@pytest.mark.asyncio
async def test_tx_by_number_and_index(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.tx_by_number_and_index(123)
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getTransactionByBlockNumberAndIndex',
                index='0x7b',
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_hex', new=Mock()) as hex_mock:
            with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
                await proxy.tx_by_number_and_index(123, 456)
                hex_mock.assert_called_once_with(123)
                tag_mock.assert_called_once_with(456)
                mock.assert_called_once()


@pytest.mark.asyncio
async def test_tx_count(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.tx_count('addr')
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getTransactionCount',
                address='addr',
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
            await proxy.tx_count('addr', 123)
            tag_mock.assert_called_once_with(123)
            mock.assert_called_once()


@pytest.mark.asyncio
async def test_send_raw_tx(proxy):
    with patch('aioetherscan.network.Network.post', new=CoroutineMock()) as mock:
        await proxy.send_raw_tx('somehex')
        mock.assert_called_once_with(
            data=dict(
                module='proxy',
                action='eth_sendRawTransaction',
                hex='somehex',
            )
        )


@pytest.mark.asyncio
async def test_tx_receipt(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.tx_receipt('0x123')
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getTransactionReceipt',
                txhash='0x123',
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_hex', new=Mock()) as hex_mock:
            await proxy.tx_receipt('0x123')
            hex_mock.assert_called_once_with('0x123')
            mock.assert_called_once()


@pytest.mark.asyncio
async def test_call(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.call('0x123', '0x456')
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_call',
                to='0x123',
                data='0x456',
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_hex', new=Mock()) as hex_mock:
            with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
                await proxy.call('0x123', '0x456', '0x789')
                hex_mock.assert_has_calls([call('0x123'), call('0x456')])
                tag_mock.assert_called_once_with('0x789')
                mock.assert_called_once()


@pytest.mark.asyncio
async def test_code(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.code('addr')
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getCode',
                address='addr',
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
            await proxy.code('addr', 123)
            tag_mock.assert_called_once_with(123)
            mock.assert_called_once()


@pytest.mark.asyncio
async def test_storage_at(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.storage_at('addr', 'pos')
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_getStorageAt',
                address='addr',
                position='pos',
                tag='latest'
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_tag', new=Mock()) as tag_mock:
            await proxy.storage_at('addr', 'pos', 123)
            tag_mock.assert_called_once_with(123)
            mock.assert_called_once()


@pytest.mark.asyncio
async def test_gas_price(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.gas_price()
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_gasPrice',
            )
        )


@pytest.mark.asyncio
async def test_estimate_gas(proxy):
    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        await proxy.estimate_gas(
            to='0x123',
            value='val',
            gas_price='123',
            gas='456'
        )
        mock.assert_called_once_with(
            params=dict(
                module='proxy',
                action='eth_estimateGas',
                to='0x123',
                value='val',
                gasPrice='123',
                gas='456',
            )
        )

    with patch('aioetherscan.network.Network.get', new=CoroutineMock()) as mock:
        with patch('aioetherscan.modules.proxy.check_hex', new=Mock()) as hex_mock:
            await proxy.estimate_gas(
                to='0x123',
                value='val',
                gas_price='123',
                gas='456'
            )
            hex_mock.assert_called_once_with('0x123')
            mock.assert_called_once()
