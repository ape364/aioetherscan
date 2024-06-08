from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:  # pragma: no cover
    from aioetherscan.modules.extra.generators.blocks_parser import Transfer


def tx_block_number(tx: dict) -> int:
    return int(tx['blockNumber'])


def drop_block(transfers: list['Transfer'], block_number: int) -> Iterable['Transfer']:
    return filter(lambda x: tx_block_number(x) != block_number, transfers)


def get_max_block_number(transfers: list['Transfer']) -> int:
    tx_with_max_block_number = max(transfers, key=tx_block_number)
    return tx_block_number(tx_with_max_block_number)
