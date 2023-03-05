from unittest.mock import MagicMock

import pytest

from aioetherscan.modules.extra.links import LinkHelper


@pytest.fixture
def ub():
    url_builder_mock = MagicMock()
    yield url_builder_mock


@pytest.fixture
def lh(ub):
    lh = LinkHelper(ub)
    yield lh


def test_get_address_link(lh, ub):
    address = 'some_address'
    lh.get_address_link(address)
    ub.get_link.assert_called_once_with(f'address/{address}')


def test_get_tx_link(lh, ub):
    tx = '0x123'
    lh.get_tx_link(tx)
    ub.get_link.assert_called_once_with(f'tx/{tx}')


def test_get_block_link(lh, ub):
    block = 123
    lh.get_block_link(block)
    ub.get_link.assert_called_once_with(f'block/{block}')


def test_get_block_txs_link(lh, ub):
    block = 123
    lh.get_block_txs_link(block)
    ub.get_link.assert_called_once_with(f'txs?block={block}')
