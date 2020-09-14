from typing import Tuple, Dict, List, Iterator, AsyncIterator, Optional

from asyncio_throttle import Throttler

from aioetherscan.exceptions import EtherscanClientApiError


class Utils:
    """Helper methods which use the combination of documented APIs."""

    def __init__(self, client):
        self._client = client

    async def token_transfers_generator(
            self,
            address: str = None,
            contract_address: str = None,
            throttler: Throttler = None,
            block_limit: int = 50,
            offset: int = 3,
            start_block: int = 0,
            end_block: int = None,
    ) -> AsyncIterator[Dict]:
        if end_block is None:
            end_block = int(await self._client.proxy.block_number(), 16)

        if throttler is None:
            throttler = Throttler(rate_limit=5, period=1.0)

        for sblock, eblock in self._generate_intervals(start_block, end_block, block_limit):
            async for transfer in self._parse_by_pages(
                    address=address,
                    contract_address=contract_address,
                    start_block=sblock,
                    end_block=eblock,
                    offset=offset,
                    throttler=throttler
            ):
                yield transfer

    async def token_transfers(
            self,
            address: str = None,
            contract_address: str = None,
            be_polite: bool = True,
            block_limit: int = 50,
            offset: int = 3,
            start_block: int = 0,
            end_block: int = None,
            throttler: Throttler = None,
    ) -> List[Dict]:
        kwargs = {k: v for k, v in locals().items() if k != 'self' and not k.startswith('_')}
        return [t async for t in self.token_transfers_generator(**kwargs)]

    async def is_contract(self, address: str) -> bool:
        try:
            response = await self._client.contract.contract_abi(address=address)
        except EtherscanClientApiError as e:
            if e.message.upper() == 'NOTOK' and e.result.lower() == 'contract source code not verified':
                return False
            raise
        else:
            return True if response else False

    async def get_contract_creator(self, contract_address: str) -> Optional[str]:
        try:
            response = await self._client.account.internal_txs(
                address=contract_address,
                start_block=1,
                page=1,
                offset=1
            )  # try to find first internal transaction
        except EtherscanClientApiError as e:
            if e.message.lower() != 'no transactions found':
                raise
            else:
                response = None

        if not response:
            try:
                response = await self._client.account.normal_txs(
                    address=contract_address,
                    start_block=1,
                    page=1,
                    offset=1
                )  # try to find first normal transaction
            except EtherscanClientApiError as e:
                if e.message.lower() != 'no transactions found':
                    raise

        return next((i['from'].lower() for i in response), None)

    async def _parse_by_pages(
            self,
            start_block: int,
            end_block: int,
            offset: int,
            throttler: Throttler = None,
            address: str = None,
            contract_address: str = None,
    ) -> AsyncIterator[Dict]:
        page = 1

        while True:
            async with throttler:
                try:
                    transfers = await self._client.account.token_transfers(
                        address=address,
                        contract_address=contract_address,
                        start_block=start_block,
                        end_block=end_block,
                        page=page,
                        offset=offset
                    )
                except EtherscanClientApiError as e:
                    if e.message == 'No transactions found':
                        break
                    raise
                else:
                    for transfer in transfers:
                        yield transfer
                    page += 1

    @staticmethod
    def _generate_intervals(from_number: int, to_number: int, count: int) -> Iterator[Tuple[int, int]]:
        for i in range(from_number, to_number + 1, count):
            yield (i, min(i + count - 1, to_number))
