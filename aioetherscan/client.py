from asyncio import AbstractEventLoop
from typing import AsyncContextManager, Union

from aiohttp import ClientTimeout
from aiohttp_retry import RetryOptionsBase

from aioetherscan.modules.account import Account
from aioetherscan.modules.block import Block
from aioetherscan.modules.contract import Contract
from aioetherscan.modules.extra import ExtraModules
from aioetherscan.modules.gas_tracker import GasTracker
from aioetherscan.modules.logs import Logs
from aioetherscan.modules.proxy import Proxy
from aioetherscan.modules.stats import Stats
from aioetherscan.modules.token import Token
from aioetherscan.modules.transaction import Transaction
from aioetherscan.network import Network, UrlBuilder


class Client:
    def __init__(
        self,
        api_key: Union[str, list[str]],
        api_kind: str = 'eth',
        network: str = 'main',
        loop: AbstractEventLoop = None,
        timeout: ClientTimeout = None,
        proxy: str = None,
        throttler: AsyncContextManager = None,
        retry_options: RetryOptionsBase = None,
    ) -> None:
        api_keys = [api_key] if isinstance(api_key, str) else api_key
        self._url_builder = UrlBuilder(api_keys, api_kind, network)
        self._http = Network(self._url_builder, loop, timeout, proxy, throttler, retry_options)

        self.account = Account(self)
        self.block = Block(self)
        self.contract = Contract(self)
        self.transaction = Transaction(self)
        self.stats = Stats(self)
        self.logs = Logs(self)
        self.proxy = Proxy(self)
        self.token = Token(self)
        self.gas_tracker = GasTracker(self)

        self.extra = ExtraModules(self, self._url_builder)

    @property
    def currency(self) -> str:
        return self._url_builder.currency

    @property
    def api_kind(self) -> str:
        return self._url_builder.api_kind.title()

    @property
    def scaner_url(self) -> str:
        return self._url_builder.BASE_URL

    async def close(self):
        await self._http.close()
