# aioetherscan

[![PyPi](https://img.shields.io/pypi/v/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![License](https://img.shields.io/pypi/l/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![Coveralls](https://img.shields.io/coveralls/ape364/aioetherscan.svg)](https://coveralls.io/github/ape364/aioetherscan)
[![Versions](https://img.shields.io/pypi/pyversions/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)


[Etherscan.io](https://etherscan.io) [API](https://etherscan.io/apis) async Python non-official wrapper.

## Features

### API modules

Supports all API modules:

* [Accounts](https://docs.etherscan.io/api-endpoints/accounts)
* [Contracts](https://docs.etherscan.io/api-endpoints/contracts)
* [Transactions](https://docs.etherscan.io/api-endpoints/stats)
* [Blocks](https://docs.etherscan.io/api-endpoints/blocks)
* [Event logs](https://docs.etherscan.io/api-endpoints/logs)
* [GETH/Parity proxy](https://docs.etherscan.io/api-endpoints/geth-parity-proxy)
* [Tokens](https://docs.etherscan.io/api-endpoints/tokens)
* [Gas Tracker](https://docs.etherscan.io/api-endpoints/gas-tracker)
* [Stats](https://docs.etherscan.io/api-endpoints/stats-1)

Also provides `extra` module, which supports:
* `link` helps to compose links to address/tx/etc
* `contract` helps to fetch contract data
* `generators` allows to fetch a lot of transactions without timeouts and not getting banned

### Blockchains

Supports blockchain explorers:

* [Etherscan](https://docs.etherscan.io/getting-started/endpoint-urls)
* [BscScan](https://docs.bscscan.com/getting-started/endpoint-urls)
* [SnowTrace](https://snowtrace.io/documentation/etherscan-compatibility/accounts)
* [PolygonScan](https://docs.polygonscan.com/getting-started/endpoint-urls)
* [Optimism](https://docs.optimism.etherscan.io/getting-started/endpoint-urls)
* [Arbiscan](https://docs.arbiscan.io/getting-started/endpoint-urls)
* [FtmScan](https://docs.ftmscan.com/getting-started/endpoint-urls)
* [Basescan](https://docs.basescan.org/getting-started/endpoint-urls)
* [Taikoscan](https://docs.taikoscan.io/getting-started/endpoint-urls)
* [SnowScan](https://docs.snowscan.xyz/getting-started/endpoint-urls)

## Installation

```sh
pip install -U aioetherscan
```

## Usage
Register Etherscan account and [create free API key](https://etherscan.io/myapikey).

```python
import asyncio
import logging

from aiohttp_retry import ExponentialRetry
from asyncio_throttle import Throttler

from aioetherscan import Client

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


async def main():
    throttler = Throttler(rate_limit=4, period=1.0)
    retry_options = ExponentialRetry(attempts=2)

    c = Client('YourApiKeyToken', throttler=throttler, retry_options=retry_options)

    try:
        print(await c.stats.eth_price())
        print(await c.block.block_reward(123456))

        address = '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2'
        async for t in c.extra.generators.token_transfers(
                address=address,
                start_block=19921833,
                end_block=19960851
        ):
            print(t)
            print(c.extra.link.get_tx_link(t['hash']))

        print(c.extra.link.get_address_link(address))
    finally:
        await c.close()


if __name__ == '__main__':
    asyncio.run(main())

```
