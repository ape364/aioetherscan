from typing import Dict, Optional
from urllib.parse import urlunsplit, urljoin


class UrlBuilder:
    _API_KINDS = {
        'eth': ('etherscan.io', 'ETH'),
        'bsc': ('bscscan.com', 'BNB'),
        'avax': ('snowtrace.io', 'AVAX'),
        'polygon': ('polygonscan.com', 'MATIC'),
        'optimism': ('etherscan.io', 'ETH'),
        'arbitrum': ('arbiscan.io', 'ETH'),
        'fantom': ('ftmscan.com', 'FTM'),
    }

    BASE_URL: str = None
    API_URL: str = None

    def __init__(self, api_key: str, api_kind: str, network: str) -> None:
        self._API_KEY = api_key

        self._set_api_kind(api_kind)
        self._network = network.lower().strip()

        self.API_URL = self._get_api_url()
        self.BASE_URL = self._get_base_url()

    def _set_api_kind(self, api_kind: str) -> None:
        api_kind = api_kind.lower().strip()
        if api_kind not in self._API_KINDS:
            raise ValueError(
                f'Incorrect api_kind {api_kind!r}, supported only: {", ".join(self._API_KINDS)}'
            )
        else:
            self._api_kind = api_kind

    @property
    def _is_main(self) -> bool:
        return self._network == 'main'

    @property
    def _base_netloc(self) -> str:
        netloc, _ = self._API_KINDS[self._api_kind]
        return netloc

    @property
    def currency(self) -> str:
        _, currency = self._API_KINDS[self._api_kind]
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
        prefix = prefix_exceptions.get((self._api_kind, self._is_main), default_prefix)

        return self._build_url(prefix, 'api')

    def _get_base_url(self) -> str:
        network_exceptions = {('polygon', 'testnet'): 'mumbai'}
        network = network_exceptions.get((self._api_kind, self._network), self._network)

        prefix_exceptions = {
            ('optimism', True): 'optimistic',
            ('optimism', False): f'{network}-optimism',
        }
        default_prefix = None if self._is_main else network
        prefix = prefix_exceptions.get((self._api_kind, self._is_main), default_prefix)

        return self._build_url(prefix)

    def filter_and_sign(self, params: Dict):
        return self._sign(self._filter_params(params or {}))

    def _sign(self, params: Dict) -> Dict:
        if not params:
            params = {}
        params['apikey'] = self._API_KEY
        return params

    @staticmethod
    def _filter_params(params: Dict) -> Dict:
        return {k: v for k, v in params.items() if v is not None}
