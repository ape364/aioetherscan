from typing import TYPE_CHECKING

from aioetherscan.modules.extra.contract import ContractUtils
from aioetherscan.modules.extra.generators.account_proxy import GeneratorUtils
from aioetherscan.modules.extra.link import LinkUtils
from aioetherscan.url_builder import UrlBuilder

if TYPE_CHECKING:
    from aioetherscan import Client


class ExtraModules:
    def __init__(self, client: 'Client', url_builder: UrlBuilder):
        self._client = client
        self._url_builder = url_builder

        self.link = LinkUtils(self._url_builder)
        self.contract = ContractUtils(self._client)
        self.generators = GeneratorUtils(self._client)
