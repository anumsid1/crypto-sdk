# test/test_api.py
#
# Tests for the FastAPI routes using a fake adapter and in-memory database.
# No real API calls, no real database file — fast and isolated.

import pytest
from fastapi.testclient import TestClient
from typing import List, Optional
from datetime import datetime, timezone

from crypto_sdk.adapters.base import MarketDataAdapter
from crypto_sdk.models import CryptoAsset
from crypto_sdk.database import Base, PriceSnapshot, PriceAlert
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from server import app
import api.routes as routes_module


# --- Fake adapter ---

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
def test_db():
    """
    Create a fresh in-memory SQLite database for each test.
    Patches get_session in api.routes so route handlers use the test DB.
    """
    import api.routes as routes_module

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    def test_get_session():
        return Session(test_engine)

    original_get_session = routes_module.get_session
    routes_module.get_session = test_get_session

    yield test_get_session

    routes_module.get_session = original_get_session


@pytest.fixture
def client(test_db):
    routes_module.adapter = FakeMarketDataAdapter()
    return TestClient(app)


# --- Market route tests ---

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


# --- History route tests ---

def test_get_price_history(client, test_db):
    """Seed two snapshots then verify the history endpoint returns them."""
    session = test_db()
    session.add(PriceSnapshot(
        coin_id="bitcoin", symbol="btc", name="Bitcoin",
        price=80000.0, market_cap=1_500_000_000_000,
        price_change_24h=6.5, captured_at=datetime.now(timezone.utc),
    ))
    session.add(PriceSnapshot(
        coin_id="bitcoin", symbol="btc", name="Bitcoin",
        price=81000.0, market_cap=1_510_000_000_000,
        price_change_24h=7.0, captured_at=datetime.now(timezone.utc),
    ))
    session.commit()
    session.close()

    response = client.get("/api/v1/history/bitcoin")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["coin_id"] == "bitcoin"


def test_get_price_history_not_found(client):
    """Returns 404 when no history exists for a coin."""
    response = client.get("/api/v1/history/doesnotexist")
    assert response.status_code == 404


# --- Alerts route tests ---

def test_get_alerts(client, test_db):
    """Seed one alert then verify the alerts endpoint returns it."""
    session = test_db()
    session.add(PriceAlert(
        coin_id="ethereum", symbol="eth",
        price_change_24h=8.0, price_at_alert=1600.0,
        triggered_at=datetime.now(timezone.utc),
    ))
    session.commit()
    session.close()

    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["coin_id"] == "ethereum"


def test_get_alerts_empty(client):
    """Returns empty list when no alerts have been triggered."""
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    assert response.json() == []
