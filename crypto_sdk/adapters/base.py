# crypto_sdk/adapters/base.py
#
# This is the abstract base class — the equivalent of an Elixir behaviour.
# Any adapter that fetches market data MUST implement these methods.
# This means you can swap CoinGecko for Binance, CryptoCompare, etc.
# and the API routes never need to change.

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import CryptoAsset


class MarketDataAdapter(ABC):

    @abstractmethod
    def get_market_data(
        self,
        currency: str = "usd",
        limit: int = 10,
    ) -> List[CryptoAsset]:
        """Fetch a list of crypto assets with current market data."""
        pass

    @abstractmethod
    def get_coin(self, coin_id: str, currency: str = "usd") -> Optional[CryptoAsset]:
        """Fetch a single coin by its ID (e.g. 'bitcoin')."""
        pass
