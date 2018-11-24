# aioetherscan

[![PyPi](https://img.shields.io/pypi/v/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![License](https://img.shields.io/pypi/l/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)
[![Build](https://travis-ci.com/ape364/aioetherscan.svg?branch=master)](https://travis-ci.com/ape364/aioetherscan)
[![Coveralls](https://img.shields.io/coveralls/ape364/aioetherscan.svg)](https://coveralls.io/github/ape364/aioetherscan)
[![Versions](https://img.shields.io/pypi/pyversions/aioetherscan.svg)](https://pypi.org/project/aioetherscan/)


Etherscan.io [API](https://etherscan.io/apis) async Python non-official wrapper. Tested only with Python 3.7.

## Features
Supports all API modules:

* [Accounts](https://etherscan.io/apis#accounts)
* [Contracts](https://etherscan.io/apis#contracts)
* [Transactions](https://etherscan.io/apis#transactions)
* [Blocks](https://etherscan.io/apis#blocks)
* [Event logs](https://etherscan.io/apis#logs)
* [GETH/Parity proxy](https://etherscan.io/apis#proxy)
* [Tokens](https://etherscan.io/apis#tokens)
* [Stats](https://etherscan.io/apis#stats)

Also provides 3rd party `utils` module, which allows to fetch a lot of transactions without timeouts and getting banned.

## Installation

```sh
pip install -U aioetherscan
```

## Usage
Register Etherscan account and [create free API key](https://etherscan.io/myapikey).

```python
import asyncio

from aioetherscan import Client


async def main():
    c = Client('apikey')
    try:
        print(await c.stats.eth_price())
        print(await c.block.block_reward(123456))
        async for t in c.utils.token_transfers_generator('0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2'):
            print(t)
    finally:
        await c.close()


if __name__ == '__main__':
    asyncio.run(main())
```

## TODO
* Add test networks support
