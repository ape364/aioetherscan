import asyncio

from aioetherscan.modules.account import Account
from aioetherscan.modules.block import Block
from aioetherscan.modules.contract import Contract
from aioetherscan.modules.logs import Logs
from aioetherscan.modules.proxy import Proxy
from aioetherscan.modules.stats import Stats
from aioetherscan.modules.transaction import Transaction
from aioetherscan.modules.utils import Utils
from aioetherscan.network import Network


class Client:
    def __init__(self, api_key: str, api_kind:str='eth', network: str = 'main', loop: asyncio.AbstractEventLoop = None) -> None:
        self._http = Network(api_key, api_kind, network, loop)

        self.account = Account(self)
        self.block = Block(self)
        self.contract = Contract(self)
        self.transaction = Transaction(self)
        self.stats = Stats(self)
        self.logs = Logs(self)
        self.proxy = Proxy(self)

        self.utils = Utils(self)

    async def close(self):
        await self._http.close()
