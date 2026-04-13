# Crypto SDK

A Python SDK for live cryptocurrency market data via the [CoinGecko API](https://www.coingecko.com/en/api). Includes a REST API, analytics utilities, CLI, structured logging, and a full test suite.

---

## Features

- Live market data from CoinGecko (top coins by market cap)
- Analytics — top movers, biggest gainer, average price, market cap filtering
- REST API with FastAPI and auto-generated Swagger docs
- Adapter pattern — swap data sources without changing API routes
- CLI — query market data directly from the terminal
- `.env` config — environment-based configuration
- Structured file logging with rotation
- Retry & timeout handling on all HTTP requests
- Async client via `httpx`
- Full test suite with pytest (no real API calls in tests)
- CI via GitHub Actions

---

## Project Structure

```
crypto_sdk_project/
├── crypto_sdk/
│   ├── adapters/
│   │   ├── base.py          # Abstract adapter (swap data sources)
│   │   └── coingecko.py     # CoinGecko implementation
│   ├── analytics.py         # Top movers, biggest gainer, average price
│   ├── async_client.py      # Async client using httpx
│   ├── client.py            # Sync HTTP client with retry/timeout
│   ├── logger.py            # Rotating file logger
│   └── models.py            # CryptoAsset dataclass
├── api/
│   ├── routes.py            # FastAPI route handlers
│   └── schemas.py           # Pydantic request/response models
├── test/
│   ├── test_api.py          # API route tests (fake adapter, no real calls)
│   ├── test_analytics.py    # Analytics unit tests
│   └── test_client.py       # SDK client tests
├── .env                     # Local config (see .env section below)
├── main.py                  # CLI entry point
├── server.py                # FastAPI server entry point
└── requirements.txt
```

---

## Requirements

- Python 3.11+
- pip

---

## Setup

**1. Clone the repo**

```bash
git clone <https://github.com/anumsid1/crypto-sdk.git>
cd crypto_sdk_project
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

**3. Install dependencies**

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

**4. Configure environment**

The `.env` file is already included with safe defaults:

```env
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
COINGECKO_TIMEOUT=5
COINGECKO_RETRIES=3
DEFAULT_CURRENCY=usd
DEFAULT_PER_PAGE=10
LOG_LEVEL=INFO
```

---

## Running the CLI

```bash
python3 main.py                                      # Top 10 coins in USD
python3 main.py --currency eur                       # Prices in EUR
python3 main.py --limit 20 --top-movers              # Top 20 coins, show movers >5%
python3 main.py --biggest-gainer                     # Show single biggest gainer
python3 main.py --min-market-cap 10000000000         # Filter by $10B+ market cap
python3 main.py --help                               # Show all options
```

---

## Running the REST API

```bash
python3 server.py
```

The server starts at `http://localhost:8000`.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/markets` | Top coins by market cap |
| GET | `/api/v1/markets/summary` | Market summary with average price and biggest gainer |
| GET | `/api/v1/markets/{coin_id}` | Single coin by ID (e.g. `bitcoin`, `ethereum`) |

### Query Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `currency` | `usd` | Currency to price in (`usd`, `eur`, `gbp`, etc.) |
| `limit` | `10` | Number of coins (1–250) |

### Interactive Docs

FastAPI generates live interactive docs automatically:

```
http://localhost:8000/docs
```

### Example Requests

```bash
curl http://localhost:8000/api/v1/markets
curl http://localhost:8000/api/v1/markets?currency=eur&limit=20
curl http://localhost:8000/api/v1/markets/summary
curl http://localhost:8000/api/v1/markets/bitcoin
```

---

## Running Tests

Tests use a fake adapter — no real API calls are made.

```bash
python3 -m pytest -v
```
---

## CI

Tests run automatically on every push and pull request to `main` via GitHub Actions.