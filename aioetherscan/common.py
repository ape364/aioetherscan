from datetime import date
from typing import Union, Tuple, Dict


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
        'pending',  # for the pending state/transactions
    )

    if tag in _TAGS:
        return tag
    return check_hex(tag)


def check_sort_direction(sort: str) -> str:
    _SORT_ORDERS = (
        'asc',  # ascending order
        'desc',  # descending order
    )
    return check_value(sort, _SORT_ORDERS)


def check_blocktype(blocktype: str) -> str:
    _BLOCK_TYPES = (
        'blocks',  # full blocks only
        'uncles',  # uncle blocks only
    )
    return check_value(blocktype, _BLOCK_TYPES)


def check_closest_value(closest_value: str) -> str:
    _CLOSEST_VALUES = (
        'before',  # ascending order
        'after',  # descending order
    )

    return check_value(closest_value, _CLOSEST_VALUES)


def check_client_type(client_type: str) -> str:
    _CLIENT_TYPES = (
        'geth',
        'parity',
    )

    return check_value(client_type, _CLIENT_TYPES)


def check_sync_mode(sync_mode: str) -> str:
    _SYNC_MODES = (
        'default',
        'archive',
    )

    return check_value(sync_mode, _SYNC_MODES)


def check_token_standard(token_standard: str) -> str:
    _TOKEN_STANDARDS = (
        'erc20',
        'erc721',
        'erc1155',
    )

    return check_value(token_standard, _TOKEN_STANDARDS)


def get_daily_stats_params(action: str, start_date: date, end_date: date, sort: str) -> Dict:
    return dict(
        module='stats',
        action=action,
        startdate=start_date.isoformat(),
        enddate=end_date.isoformat(),
        sort=check_sort_direction(sort),
    )
