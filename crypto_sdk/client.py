# crypto_sdk/client.py

import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .models import CryptoAsset


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()

        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )

        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)

    def fetch_market_data(self, vs_currency="usd"):
        url = f"{self.BASE_URL}/coins/markets"

        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": False,
        }

        try:
            logger.info("Fetching market data from CoinGecko...")

            response = self.session.get(url, params=params, timeout=5)

            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

        data = response.json()

        return [
            CryptoAsset(
                id=item["id"],
                symbol=item["symbol"],
                name=item["name"],
                current_price=item["current_price"],
                market_cap=item["market_cap"],
                price_change_percentage_24h=item["price_change_percentage_24h"],
            )
            for item in data
        ]
