from typing import Union, Tuple


def check_value(value: str, values: Tuple[str, ...]) -> str:
    if value and value.lower() not in values:
        raise ValueError(f'Invalid value {value!r}, only {values} are supported.')
    return value


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


def check_sort_direction(sort: str) -> str:
    _SORT_ORDERS = (
        'asc',  # ascending order
        'desc'  # descending order
    )
    return check_value(sort, _SORT_ORDERS)


def check_blocktype(blocktype: str) -> str:
    _BLOCK_TYPES = (
        'blocks',  # full blocks only
        'uncles'  # uncle blocks only
    )
    return check_value(blocktype, _BLOCK_TYPES)


def check_closest_value(closest_value: str) -> str:
    _CLOSEST_VALUEST = (
        'before',  # ascending order
        'after'  # descending order
    )

    return check_value(closest_value, _CLOSEST_VALUEST)
