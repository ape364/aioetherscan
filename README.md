# aioetherscan

[![PyPi](https://img.shields.io/pypi/v/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![License](https://img.shields.io/pypi/l/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![Build](https://travis-ci.com/ape364/aioetherscan.svg?branch=master)](https://travis-ci.com/ape364/aioetherscan)
[![Coveralls](https://img.shields.io/coveralls/ape364/aioetherscan.svg)](https://coveralls.io/github/ape364/aioetherscan)
[![Versions](https://img.shields.io/pypi/pyversions/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)


[Etherscan.io](https://etherscan.io) [API](https://etherscan.io/apis) async Python non-official wrapper. Tested with Python 3.7 & 3.8.

## Features

### API modules

Supports all API modules:

* [Accounts](https://etherscan.io/apis#accounts)
* [Contracts](https://etherscan.io/apis#contracts)
* [Transactions](https://etherscan.io/apis#transactions)
* [Blocks](https://etherscan.io/apis#blocks)
* [Event logs](https://etherscan.io/apis#logs)
* [GETH/Parity proxy](https://etherscan.io/apis#proxy)
* [Tokens](https://etherscan.io/apis#tokens)
* [Stats](https://etherscan.io/apis#stats)

Also provides 3rd party `utils` module, which allows to fetch a lot of transactions without timeouts and not getting banned.

### Networks

Supports networks:

* [Main](https://etherscan.io/)
* [Ropsten](https://ropsten.etherscan.io/)
* [Kovan](https://kovan.etherscan.io/)
* [Rinkeby](https://rinkeby.etherscan.io/)
* [Goerli](https://goerli.etherscan.io/)
* [Tobalaba](https://tobalaba.etherscan.com/)

## Installation

```sh
pip install -U aioetherscan
```

## Usage
Register Etherscan account and [create free API key](https://etherscan.io/myapikey).

```python
import asyncio

from aioetherscan import Client
from asyncio_throttle import Throttler


async def main():
    c = Client('apikey')
    throttler = Throttler(rate_limit=5, period=1.0)
    try:
        print(await c.stats.eth_price())
        print(await c.block.block_reward(123456))

        async for t in c.utils.token_transfers_generator(
            address='0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2',
            throttler=throttler
        ):
            print(t)
    finally:
        await c.close()


if __name__ == '__main__':
    asyncio.run(main())
```