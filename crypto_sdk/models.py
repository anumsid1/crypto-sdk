# crypto_sdk/models.py

from dataclasses import dataclass


@dataclass
class CryptoAsset:
    id: str
    symbol: str
    name: str
    current_price: float
    market_cap: float
    price_change_percentage_24h: float
