from urllib.parse import urlencode

from aioetherscan.url_builder import UrlBuilder


class LinkHelper:
    def __init__(self, url_builder: UrlBuilder):
        self._url_builder = url_builder

    def get_address_link(self, address: str) -> str:
        return self._url_builder.get_link(f'address/{address}')

    def get_tx_link(self, tx_hash: str) -> str:
        return self._url_builder.get_link(f'tx/{tx_hash}')

    def get_block_link(self, block_number: int) -> str:
        return self._url_builder.get_link(f'block/{block_number}')

    def get_block_txs_link(self, block_number: int) -> str:
        return self._url_builder.get_link(f'txs?{urlencode({"block": block_number})}')
