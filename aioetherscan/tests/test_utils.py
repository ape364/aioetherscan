import asynctest
import pytest
from asynctest import CoroutineMock

from aioetherscan import Client


@pytest.fixture()
async def client():
    c = Client('TestApiKey')
    yield c
    await c.close()


@pytest.fixture()
async def utils(client):
    yield client.utils


@pytest.mark.asyncio
async def test_is_contract(utils):
    with asynctest.patch('aioetherscan.modules.contract.Contract.contract_abi', new=CoroutineMock()) as mock:
        await utils.is_contract(address='addr')
        mock.assert_called_once_with(address='addr')


@pytest.mark.asyncio
async def test_get_contract_creator(utils):
    with asynctest.patch('aioetherscan.modules.account.Account.internal_txs', new=CoroutineMock()) as mock:
        await utils.get_contract_creator(contract_address='addr')
        mock.assert_called_once_with(
            address='addr',
            start_block=1,
            page=1,
            offset=1
        )


@pytest.mark.parametrize(
    "api_kind,network_name,address,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/address/qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/address/qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/address/qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/address/qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/address/qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/address/qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/address/qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/address/qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/address/qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/address/qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/address/qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/address/qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/address/qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/address/qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/address/qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/address/qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/address/qwe'),
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/address/qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/address/qwe'),
    ]
)
def test_get_address_link(api_kind, network_name, address, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_address_link(address) == expected


@pytest.mark.parametrize(
    "api_kind,network_name,tx_hash,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/tx/qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/tx/qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/tx/qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/tx/qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/tx/qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/tx/qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/tx/qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/tx/qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/tx/qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/tx/qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/tx/qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/tx/qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/tx/qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/tx/qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/tx/qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/tx/qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/tx/qwe'),
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/tx/qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/tx/qwe'),
    ]
)
def test_get_tx_link(api_kind, network_name, tx_hash, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_tx_link(tx_hash) == expected


@pytest.mark.parametrize(
    "api_kind,network_name,block_number,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/block/qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/block/qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/block/qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/block/qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/block/qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/block/qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/block/qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/block/qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/block/qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/block/qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/block/qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/block/qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/block/qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/block/qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/block/qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/block/qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/block/qwe'),
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/block/qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/block/qwe'),
    ]
)
def test_get_block_link(api_kind, network_name, block_number, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_block_link(block_number) == expected


@pytest.mark.parametrize(
    "api_kind,network_name,block_number,expected",
    [
        ('eth', 'main', 'qwe', 'https://etherscan.io/txs?block=qwe'),
        ('eth', 'ropsten', 'qwe', 'https://ropsten.etherscan.io/txs?block=qwe'),
        ('eth', 'kovan', 'qwe', 'https://kovan.etherscan.io/txs?block=qwe'),
        ('eth', 'rinkeby', 'qwe', 'https://rinkeby.etherscan.io/txs?block=qwe'),
        ('eth', 'goerli', 'qwe', 'https://goerli.etherscan.io/txs?block=qwe'),
        ('eth', 'sepolia', 'qwe', 'https://sepolia.etherscan.io/txs?block=qwe'),
        ('bsc', 'main', 'qwe', 'https://bscscan.com/txs?block=qwe'),
        ('bsc', 'testnet', 'qwe', 'https://testnet.bscscan.com/txs?block=qwe'),
        ('avax', 'main', 'qwe', 'https://snowtrace.io/txs?block=qwe'),
        ('avax', 'testnet', 'qwe', 'https://testnet.snowtrace.io/txs?block=qwe'),
        ('polygon', 'main', 'qwe', 'https://polygonscan.com/txs?block=qwe'),
        ('polygon', 'testnet', 'qwe', 'https://mumbai.polygonscan.com/txs?block=qwe'),
        ('optimism', 'main', 'qwe', 'https://optimistic.etherscan.io/txs?block=qwe'),
        ('optimism', 'goerli', 'qwe', 'https://goerli-optimism.etherscan.io/txs?block=qwe'),
        ('arbitrum', 'main', 'qwe', 'https://arbiscan.io/txs?block=qwe'),
        ('arbitrum', 'nova', 'qwe', 'https://nova.arbiscan.io/txs?block=qwe'),
        ('arbitrum', 'goerli', 'qwe', 'https://goerli.arbiscan.io/txs?block=qwe'),
        ('fantom', 'main', 'qwe', 'https://ftmscan.com/txs?block=qwe'),
        ('fantom', 'testnet', 'qwe', 'https://testnet.ftmscan.com/txs?block=qwe'),
    ]
)
def test_get_block_txs_link(api_kind, network_name, block_number, expected):
    c = Client('TestApiKey', api_kind=api_kind, network=network_name)
    assert c.utils.get_block_txs_link(block_number) == expected
