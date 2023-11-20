from unittest.mock import Mock, patch

import pytest

from aioetherscan.common import (
    check_hex,
    check_tag,
    check_value,
    check_sort_direction,
    check_blocktype,
    check_client_type,
    check_sync_mode,
)


def test_check_hex():
    assert check_hex(123) == '0x7b'
    assert check_hex(0x7B) == '0x7b'
    assert check_hex('0x7b') == '0x7b'
    with pytest.raises(ValueError):
        check_hex('wrong')


def test_check_tag():
    assert check_tag('latest') == 'latest'
    assert check_tag('earliest') == 'earliest'
    assert check_tag('pending') == 'pending'

    with patch('aioetherscan.common.check_hex', new=Mock()) as mock:
        check_tag(123)
        mock.assert_called_once_with(123)


def test_check():
    assert check_value('a', ('a', 'b')) == 'a'
    assert check_value('A', ('a', 'b')) == 'A'
    with pytest.raises(ValueError):
        check_value('c', ('a', 'b'))
    with pytest.raises(ValueError):
        check_value('C', ('a', 'b'))


def test_check_sort_direction():
    assert check_sort_direction('asc') == 'asc'
    assert check_sort_direction('desc') == 'desc'
    with pytest.raises(ValueError):
        check_sort_direction('wrong')


def test_check_blocktype():
    assert check_blocktype('blocks') == 'blocks'
    assert check_blocktype('uncles') == 'uncles'
    with pytest.raises(ValueError):
        check_blocktype('wrong')


def test_check_client_type():
    assert check_client_type('geth') == 'geth'
    assert check_client_type('parity') == 'parity'
    with pytest.raises(ValueError):
        check_client_type('wrong')


def test_check_sync_mode():
    assert check_sync_mode('default') == 'default'
    assert check_sync_mode('archive') == 'archive'
    with pytest.raises(ValueError):
        check_sync_mode('wrong')
