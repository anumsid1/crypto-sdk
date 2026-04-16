# api/routes.py
#
# FastAPI routes — these are the HTTP endpoints.
# They only talk to the adapter, never directly to CoinGeckoClient.
# This is the same separation you'd have in a Phoenix controller in Elixir.

from fastapi import APIRouter, HTTPException, Query
from crypto_sdk.adapters.coingecko import CoinGeckoAdapter
from crypto_sdk.analytics import average_price, biggest_gainer
from crypto_sdk.database import get_session, PriceSnapshot, PriceAlert
from sqlalchemy import desc
from .schemas import CryptoAssetResponse, MarketSummaryResponse, PriceSnapshotResponse, PriceAlertResponse

router = APIRouter()
adapter = CoinGeckoAdapter()


@router.get("/markets", response_model=list[CryptoAssetResponse])
def get_markets(
    currency: str = Query(default="usd", description="Currency (e.g. usd, eur, gbp)"),
    limit: int = Query(default=10, ge=1, le=250, description="Number of coins to return"),
):
    """Return a list of top coins by market cap."""
    assets = adapter.get_market_data(currency=currency, limit=limit)
    return assets


@router.get("/markets/summary", response_model=MarketSummaryResponse)
def get_summary(
    currency: str = Query(default="usd"),
    limit: int = Query(default=10, ge=1, le=250),
):
    """Return market summary including average price and biggest gainer."""
    assets = adapter.get_market_data(currency=currency, limit=limit)
    gainer = biggest_gainer(assets)

    return MarketSummaryResponse(
        currency=currency,
        total_coins=len(assets),
        average_price=average_price(assets),
        biggest_gainer=gainer,
        assets=assets,
    )


@router.get("/markets/{coin_id}", response_model=CryptoAssetResponse)
def get_coin(coin_id: str, currency: str = Query(default="usd")):
    """Return data for a single coin by ID (e.g. bitcoin, ethereum)."""
    asset = adapter.get_coin(coin_id=coin_id, currency=currency)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Coin '{coin_id}' not found")
    return asset


@router.get("/history/{coin_id}", response_model=list[PriceSnapshotResponse])
def get_price_history(
    coin_id: str,
    limit: int = Query(default=20, ge=1, le=100, description="Number of snapshots to return"),
):
    """Return stored price history for a coin from the database."""
    session = get_session()
    try:
        snapshots = (
            session.query(PriceSnapshot)
            .filter(PriceSnapshot.coin_id == coin_id)
            .order_by(desc(PriceSnapshot.captured_at))
            .limit(limit)
            .all()
        )
        if not snapshots:
            raise HTTPException(status_code=404, detail=f"No history found for '{coin_id}'")
        return [
            PriceSnapshotResponse(
                coin_id=s.coin_id,
                symbol=s.symbol,
                name=s.name,
                price=s.price,
                market_cap=s.market_cap,
                price_change_24h=s.price_change_24h,
                captured_at=s.captured_at.isoformat(),
            )
            for s in snapshots
        ]
    finally:
        session.close()


@router.get("/alerts", response_model=list[PriceAlertResponse])
def get_alerts(
    limit: int = Query(default=20, ge=1, le=100, description="Number of alerts to return"),
):
    """Return recent price alerts triggered by the background job."""
    session = get_session()
    try:
        alerts = (
            session.query(PriceAlert)
            .order_by(desc(PriceAlert.triggered_at))
            .limit(limit)
            .all()
        )
        return [
            PriceAlertResponse(
                coin_id=a.coin_id,
                symbol=a.symbol,
                price_change_24h=a.price_change_24h,
                price_at_alert=a.price_at_alert,
                triggered_at=a.triggered_at.isoformat(),
            )
            for a in alerts
        ]
    finally:
        session.close()
