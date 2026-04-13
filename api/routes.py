# api/routes.py
#
# FastAPI routes — these are the HTTP endpoints.
# They only talk to the adapter, never directly to CoinGeckoClient.
# This is the same separation you'd have in a Phoenix controller in Elixir.

from fastapi import APIRouter, HTTPException, Query
from crypto_sdk.adapters.coingecko import CoinGeckoAdapter
from crypto_sdk.analytics import average_price, biggest_gainer
from .schemas import CryptoAssetResponse, MarketSummaryResponse

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
