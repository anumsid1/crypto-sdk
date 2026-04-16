# api/schemas.py
#
# Pydantic models define the shape of API responses.
# FastAPI uses these to validate output and auto-generate docs.
# Similar to Ecto schemas in Elixir — they define the contract.

from pydantic import BaseModel, ConfigDict


class CryptoAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: float
    price_change_percentage_24h: float


class MarketSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    currency: str
    total_coins: int
    average_price: float
    biggest_gainer: CryptoAssetResponse | None
    assets: list[CryptoAssetResponse]


class PriceSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    coin_id: str
    symbol: str
    name: str
    price: float
    market_cap: float
    price_change_24h: float
    captured_at: str


class PriceAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    coin_id: str
    symbol: str
    price_change_24h: float
    price_at_alert: float
    triggered_at: str
