from aioetherscan.exceptions import EtherscanClientContentTypeError, EtherscanClientApiError, EtherscanClientProxyError


def test_content_type_error():
    e = EtherscanClientContentTypeError(1, 2)
    assert e.status == 1
    assert e.content == 2
    assert str(e) == '[1] 2'


def test_api_error():
    e = EtherscanClientApiError(1, 2)
    assert e.message == 1
    assert e.result == 2
    assert str(e) == '[1] 2'


def test_proxy_error():
    e = EtherscanClientProxyError(1, 2)
    assert e.code == 1
    assert e.message == 2
    assert str(e) == '[1] 2'
