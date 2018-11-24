from typing import Union


def check_hex(number: Union[str, int]) -> str:
    if isinstance(number, int):
        return hex(number)
    try:
        int(number, 16)
    except ValueError as e:
        raise ValueError(f'Invalid hex parameter {number!r}: {e}')
    else:
        return number


def check_tag(tag: Union[str, int]) -> str:
    _TAGS = (
        'earliest',  # the earliest/genesis block
        'latest',  # the latest mined block
        'pending'  # for the pending state/transactions
    )

    if tag in _TAGS:
        return tag
    return check_hex(tag)
