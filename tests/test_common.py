from unittest.mock import Mock, patch

import pytest

from aioetherscan.common import check_hex, check_tag


def test_check_hex():
    assert check_hex(123) == '0x7b'
    assert check_hex(0x7b) == '0x7b'
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
