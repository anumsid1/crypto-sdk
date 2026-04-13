# test/test_api.py
#
# Tests for the FastAPI routes using a fake adapter.
# The fake adapter implements MarketDataAdapter but returns hardcoded data.
# This means tests never hit the real CoinGecko API — fast and reliable.

import pytest
from fastapi.testclient import TestClient
from typing import List, Optional

from crypto_sdk.adapters.base import MarketDataAdapter
from crypto_sdk.models import CryptoAsset
from server import app
import api.routes as routes_module

FAKE_ASSETS = [
    CryptoAsset(
        id="bitcoin",
        symbol="btc",
        name="Bitcoin",
        current_price=80000.0,
        market_cap=1_500_000_000_000,
        price_change_percentage_24h=6.5,
    ),
    CryptoAsset(
        id="ethereum",
        symbol="eth",
        name="Ethereum",
        current_price=1600.0,
        market_cap=200_000_000_000,
        price_change_percentage_24h=8.0,
    ),
    CryptoAsset(
        id="tether",
        symbol="usdt",
        name="Tether",
        current_price=1.0,
        market_cap=100_000_000_000,
        price_change_percentage_24h=0.01,
    ),
]


class FakeMarketDataAdapter(MarketDataAdapter):
    def get_market_data(self, currency: str = "usd", limit: int = 10) -> List[CryptoAsset]:
        return FAKE_ASSETS[:limit]

    def get_coin(self, coin_id: str, currency: str = "usd") -> Optional[CryptoAsset]:
        for asset in FAKE_ASSETS:
            if asset.id == coin_id:
                return asset
        return None


# --- Fixtures ---

@pytest.fixture
def client():
    # Swap the real adapter for the fake one before each test
    routes_module.adapter = FakeMarketDataAdapter()
    return TestClient(app)


# --- Tests ---

def test_get_markets_returns_list(client):
    response = client.get("/api/v1/markets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "bitcoin"
    assert data[0]["current_price"] == 80000.0


def test_get_markets_limit(client):
    response = client.get("/api/v1/markets?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_summary(client):
    response = client.get("/api/v1/markets/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_coins"] == 3
    assert data["biggest_gainer"]["id"] == "ethereum"
    assert data["currency"] == "usd"


def test_get_coin_found(client):
    response = client.get("/api/v1/markets/bitcoin")
    assert response.status_code == 200
    assert response.json()["id"] == "bitcoin"


def test_get_coin_not_found(client):
    response = client.get("/api/v1/markets/doesnotexist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]