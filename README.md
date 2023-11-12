# aioetherscan

[![PyPi](https://img.shields.io/pypi/v/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![License](https://img.shields.io/pypi/l/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![Coveralls](https://img.shields.io/coveralls/ape364/aioetherscan.svg)](https://coveralls.io/github/ape364/aioetherscan)
[![Versions](https://img.shields.io/pypi/pyversions/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)


[Etherscan.io](https://etherscan.io) [API](https://etherscan.io/apis) async Python non-official wrapper.

## Features

### API modules

Supports API modules:

* [Accounts](https://docs.etherscan.io/api-endpoints/accounts)
* [Contracts](https://docs.etherscan.io/api-endpoints/contracts)
* [Transactions](https://docs.etherscan.io/api-endpoints/stats)
* [Blocks](https://docs.etherscan.io/api-endpoints/blocks)
* [Event logs](https://docs.etherscan.io/api-endpoints/logs)
* [GETH/Parity proxy](https://docs.etherscan.io/api-endpoints/geth-parity-proxy)
* [Tokens](https://docs.etherscan.io/api-endpoints/tokens)
* [Stats](https://docs.etherscan.io/api-endpoints/stats-1)

Also provides extra modules:
* `utils` allows to fetch a lot of transactions without timeouts and not getting banned
* `links` helps to compose links to address/tx/etc

### Blockchains

Supports blockchain explorers:

* [Etherscan](https://docs.etherscan.io/getting-started/endpoint-urls)
* [BscScan](https://docs.bscscan.com/getting-started/endpoint-urls)
* [SnowTrace](https://docs.snowtrace.io/getting-started/endpoint-urls)
* [PolygonScan](https://docs.polygonscan.com/getting-started/endpoint-urls)
* [Optimism](https://docs.optimism.etherscan.io/getting-started/endpoint-urls)
* [Arbiscan](https://docs.arbiscan.io/getting-started/endpoint-urls)
* [FtmScan](https://docs.ftmscan.com/getting-started/endpoint-urls)

## Installation

```sh
pip install -U aioetherscan
```

## Usage
Register Etherscan account and [create free API key](https://etherscan.io/myapikey).

```python
import asyncio

from aiohttp_retry import ExponentialRetry
from asyncio_throttle import Throttler

from aioetherscan import Client


async def main():
    throttler = Throttler(rate_limit=1, period=6.0)
    retry_options = ExponentialRetry(attempts=2)

    c = Client('YourApiKeyToken', throttler=throttler, retry_options=retry_options)

    try:
        print(await c.stats.eth_price())
        print(await c.block.block_reward(123456))

        async for t in c.utils.token_transfers_generator(
                address='0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2',
                start_block=16734850,
                end_block=16734850
        ):
            print(t)
    finally:
        await c.close()


if __name__ == '__main__':
    asyncio.run(main())
```
