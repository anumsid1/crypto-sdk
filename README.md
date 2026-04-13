# Crypto SDK

  A crypto price SDK that hits the CoinGecko public API, parses responses into dataclasses, and has basic analytics (top movers, average price, etc). It also has an async variant with httpx. 

## Features

- Fetch market data from CoinGecko
- Analytics utilities
- Retry & timeout handling
- Caching support
- Async client
- Unit tests

## Installation

- `rm -rf venv`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -e .`
- `pip install build`
- `python -m build`


## Testing
- `cd crypto_sdk_project`
-  Run `python main.py`
- `python3 -m pip install requests`
- `pip install pytest`
- `python -m pytest`
