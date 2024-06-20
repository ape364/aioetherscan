from unittest.mock import patch

import pytest
import pytest_asyncio

from aioetherscan.url_builder import UrlBuilder


def apikey():
    return 'test_api_key'


@pytest_asyncio.fixture
async def ub():
    ub = UrlBuilder(apikey(), 'eth', 'main')
    yield ub


def test_sign(ub):
    assert ub._sign({}) == {'apikey': ub._API_KEY}
    assert ub._sign({'something': 'something'}) == {'something': 'something', 'apikey': ub._API_KEY}


def test_filter_params(ub):
    assert ub._filter_params({}) == {}
    assert ub._filter_params({1: 2, 3: None}) == {1: 2}
    assert ub._filter_params({1: 2, 3: 0}) == {1: 2, 3: 0}
    assert ub._filter_params({1: 2, 3: False}) == {1: 2, 3: False}


@pytest.mark.parametrize(
    'api_kind,network_name,expected',
    [
        ('eth', 'main', 'https://api.etherscan.io/api'),
        ('eth', 'ropsten', 'https://api-ropsten.etherscan.io/api'),
        ('eth', 'kovan', 'https://api-kovan.etherscan.io/api'),
        ('eth', 'rinkeby', 'https://api-rinkeby.etherscan.io/api'),
        ('eth', 'goerli', 'https://api-goerli.etherscan.io/api'),
        ('eth', 'sepolia', 'https://api-sepolia.etherscan.io/api'),
        ('bsc', 'main', 'https://api.bscscan.com/api'),
        ('bsc', 'testnet', 'https://api-testnet.bscscan.com/api'),
        ('avax', 'main', 'https://api.snowtrace.io/api'),
        ('avax', 'testnet', 'https://api-testnet.snowtrace.io/api'),
        ('polygon', 'main', 'https://api.polygonscan.com/api'),
        ('polygon', 'testnet', 'https://api-testnet.polygonscan.com/api'),
        ('optimism', 'main', 'https://api-optimistic.etherscan.io/api'),
        ('optimism', 'goerli', 'https://api-goerli-optimistic.etherscan.io/api'),
        ('base', 'main', 'https://api.basescan.org/api'),
        ('base', 'sepolia', 'https://api-sepolia.basescan.org/api'),
        ('base', 'goerli', 'https://api-goerli.basescan.org/api'),
        ('arbitrum', 'main', 'https://api.arbiscan.io/api'),
        ('arbitrum', 'nova', 'https://api-nova.arbiscan.io/api'),
        ('arbitrum', 'goerli', 'https://api-goerli.arbiscan.io/api'),
        ('fantom', 'main', 'https://api.ftmscan.com/api'),
        ('fantom', 'testnet', 'https://api-testnet.ftmscan.com/api'),
        ('taiko', 'main', 'https://api.taikoscan.io/api'),
        ('taiko', 'hekla', 'https://api-hekla.taikoscan.io/api'),
    ],
)
def test_api_url(api_kind, network_name, expected):
    ub = UrlBuilder(apikey(), api_kind, network_name)
    assert ub.API_URL == expected


@pytest.mark.parametrize(
    'api_kind,network_name,expected',
    [
        ('eth', 'main', 'https://etherscan.io'),
        ('eth', 'ropsten', 'https://ropsten.etherscan.io'),
        ('eth', 'kovan', 'https://kovan.etherscan.io'),
        ('eth', 'rinkeby', 'https://rinkeby.etherscan.io'),
        ('eth', 'goerli', 'https://goerli.etherscan.io'),
        ('eth', 'sepolia', 'https://sepolia.etherscan.io'),
        ('bsc', 'main', 'https://bscscan.com'),
        ('bsc', 'testnet', 'https://testnet.bscscan.com'),
        ('avax', 'main', 'https://snowtrace.io'),
        ('avax', 'testnet', 'https://testnet.snowtrace.io'),
        ('polygon', 'main', 'https://polygonscan.com'),
        ('polygon', 'testnet', 'https://mumbai.polygonscan.com'),
        ('optimism', 'main', 'https://optimistic.etherscan.io'),
        ('optimism', 'goerli', 'https://goerli-optimism.etherscan.io'),
        ('base', 'main', 'https://basescan.org'),
        ('base', 'sepolia', 'https://sepolia.basescan.org'),
        ('base', 'goerli', 'https://goerli.basescan.org'),
        ('arbitrum', 'main', 'https://arbiscan.io'),
        ('arbitrum', 'nova', 'https://nova.arbiscan.io'),
        ('arbitrum', 'goerli', 'https://goerli.arbiscan.io'),
        ('fantom', 'main', 'https://ftmscan.com'),
        ('fantom', 'testnet', 'https://testnet.ftmscan.com'),
        ('taiko', 'main', 'https://taikoscan.io'),
        ('taiko', 'hekla', 'https://hekla.taikoscan.io'),
    ],
)
def test_base_url(api_kind, network_name, expected):
    ub = UrlBuilder(apikey(), api_kind, network_name)
    assert ub.BASE_URL == expected


def test_invalid_api_kind():
    with pytest.raises(ValueError) as exception:
        UrlBuilder(apikey(), 'wrong', 'main')
    assert 'Incorrect api_kind' in str(exception.value)


@pytest.mark.parametrize(
    'api_kind,expected',
    [
        ('eth', 'ETH'),
        ('bsc', 'BNB'),
        ('avax', 'AVAX'),
        ('polygon', 'MATIC'),
        ('optimism', 'ETH'),
        ('base', 'ETH'),
        ('arbitrum', 'ETH'),
        ('fantom', 'FTM'),
        ('taiko', 'ETH'),
    ],
)
def test_currency(api_kind, expected):
    ub = UrlBuilder(apikey(), api_kind, 'main')
    assert ub.currency == expected


def test_get_link(ub):
    with patch('aioetherscan.url_builder.urljoin') as join_mock:
        path = 'some_path'
        ub.get_link(path)
        join_mock.assert_called_once_with(ub.BASE_URL, path)
