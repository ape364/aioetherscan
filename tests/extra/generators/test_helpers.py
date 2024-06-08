from aioetherscan.modules.extra.generators.helpers import (
    tx_block_number,
    drop_block,
    get_max_block_number,
)


def test_tx_block_number():
    block_number = 123
    tx = dict(blockNumber=block_number)
    result = tx_block_number(tx)
    assert block_number == result
    assert isinstance(result, int)


def test_drop_block():
    block_to_drop = 456
    transfers = [
        dict(blockNumber=123),
        dict(blockNumber=456),
        dict(blockNumber=456),
        dict(blockNumber=789),
    ]

    result = list(drop_block(transfers, block_to_drop))

    for tx in transfers:
        if tx['blockNumber'] == block_to_drop:
            assert tx not in result
        else:
            assert tx in result


def test_get_max_block_number():
    max_block_number = 2**16
    transfers = [
        dict(blockNumber=123),
        dict(blockNumber=max_block_number),
        dict(blockNumber=456),
    ]

    assert get_max_block_number(transfers) == max_block_number
