import logging
from itertools import cycle
from typing import Optional
from urllib.parse import urlunsplit, urljoin


class UrlBuilder:
    _API_KINDS = {
        'eth': ('etherscan.io', 'ETH'),
        'bsc': ('bscscan.com', 'BNB'),
        'avax': ('snowtrace.io', 'AVAX'),
        'polygon': ('polygonscan.com', 'MATIC'),
        'optimism': ('etherscan.io', 'ETH'),
        'base': ('basescan.org', 'ETH'),
        'arbitrum': ('arbiscan.io', 'ETH'),
        'fantom': ('ftmscan.com', 'FTM'),
        'taiko': ('taikoscan.io', 'ETH'),
        'snowscan': ('snowscan.xyz', 'AVAX'),
    }

    BASE_URL: str = None
    API_URL: str = None

    def __init__(self, api_keys: list[str], api_kind: str, network: str) -> None:
        self._api_keys = api_keys
        self._api_keys_cycle = cycle(self._api_keys)
        self._api_key = self._get_next_api_key()

        self._set_api_kind(api_kind)
        self._network = network.lower().strip()

        self.API_URL = self._get_api_url()
        self.BASE_URL = self._get_base_url()

        self._logger = logging.getLogger(__name__)

    def _set_api_kind(self, api_kind: str) -> None:
        api_kind = api_kind.lower().strip()
        if api_kind not in self._API_KINDS:
            raise ValueError(
                f'Incorrect api_kind {api_kind!r}, supported only: {", ".join(self._API_KINDS)}'
            )
        else:
            self.api_kind = api_kind

    @property
    def _is_main(self) -> bool:
        return self._network == 'main'

    @property
    def _base_netloc(self) -> str:
        netloc, _ = self._API_KINDS[self.api_kind]
        return netloc

    @property
    def currency(self) -> str:
        _, currency = self._API_KINDS[self.api_kind]
        return currency

    def get_link(self, path: str) -> str:
        return urljoin(self.BASE_URL, path)

    def _build_url(self, prefix: Optional[str], path: str = '') -> str:
        netloc = self._base_netloc if prefix is None else f'{prefix}.{self._base_netloc}'
        return urlunsplit(('https', netloc, path, '', ''))

    def _get_api_url(self) -> str:
        prefix_exceptions = {
            ('optimism', True): 'api-optimistic',
            ('optimism', False): f'api-{self._network}-optimistic',
        }
        default_prefix = 'api' if self._is_main else f'api-{self._network}'
        prefix = prefix_exceptions.get((self.api_kind, self._is_main), default_prefix)

        return self._build_url(prefix, 'api')

    def _get_base_url(self) -> str:
        network_exceptions = {('polygon', 'testnet'): 'mumbai'}
        network = network_exceptions.get((self.api_kind, self._network), self._network)

        prefix_exceptions = {
            ('optimism', True): 'optimistic',
            ('optimism', False): f'{network}-optimism',
        }
        default_prefix = None if self._is_main else network
        prefix = prefix_exceptions.get((self.api_kind, self._is_main), default_prefix)

        return self._build_url(prefix)

    def filter_and_sign(self, params: dict):
        return self._sign(self._filter_params(params or {}))

    def _sign(self, params: dict) -> dict:
        if not params:
            params = {}
        params['apikey'] = self._api_key
        return params

    @staticmethod
    def _filter_params(params: dict) -> dict:
        return {k: v for k, v in params.items() if v is not None}

    def _get_next_api_key(self) -> str:
        return next(self._api_keys_cycle)

    def rotate_api_key(self) -> None:
        prev_api_key = self._api_key
        next_api_key = self._get_next_api_key()

        self._logger.info(
            f'Rotating API key from {self._mask_api_key(prev_api_key)} to {self._mask_api_key(next_api_key)}'
        )

        self._api_key = next_api_key

    @staticmethod
    def _mask_api_key(api_key: str, masked_chars_count: int = 4) -> str:
        return '*' * (len(api_key) - masked_chars_count) + api_key[-masked_chars_count:]

    @property
    def keys_count(self) -> int:
        return len(self._api_keys)
