# crypto_sdk/adapters/coingecko.py
#
# CoinGecko implementation of MarketDataAdapter.
# This is the only file that knows about CoinGeckoClient.
# To add a Binance adapter, create binance.py implementing the same base class.

from typing import List, Optional
from ..client import CoinGeckoClient
from ..models import CryptoAsset
from .base import MarketDataAdapter


class CoinGeckoAdapter(MarketDataAdapter):

    def __init__(self):
        self.client = CoinGeckoClient()

    def get_market_data(self, currency: str = "usd", limit: int = 10) -> List[CryptoAsset]:
        return self.client.fetch_market_data(vs_currency=currency, per_page=limit)

    def get_coin(self, coin_id: str, currency: str = "usd") -> Optional[CryptoAsset]:
        assets = self.client.fetch_market_data(vs_currency=currency, per_page=250)
        for asset in assets:
            if asset.id == coin_id:
                return asset
        return None
