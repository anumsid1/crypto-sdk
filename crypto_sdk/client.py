# crypto_sdk/client.py

import os
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from .models import CryptoAsset

load_dotenv()

logger = logging.getLogger(__name__)


class CryptoAPIError(Exception):
    """Base exception for Crypto SDK errors."""
    pass


class CoinGeckoClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
        self.timeout = int(os.getenv("COINGECKO_TIMEOUT", 5))
        retries = int(os.getenv("COINGECKO_RETRIES", 3))

        self.session = requests.Session()

        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_market_data(self, vs_currency=None, per_page=None):
        url = f"{self.base_url}/coins/markets"

        params = {
            "vs_currency": vs_currency or os.getenv("DEFAULT_CURRENCY", "usd"),
            "order": "market_cap_desc",
            "per_page": per_page or int(os.getenv("DEFAULT_PER_PAGE", 10)),
            "page": 1,
            "sparkline": False,
        }

        try:
            logger.info("Fetching market data from CoinGecko...")

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            raise CryptoAPIError("Request to CoinGecko timed out")

        except requests.exceptions.ConnectionError:
            logger.error("Connection failed")
            raise CryptoAPIError("Failed to connect to CoinGecko API")

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise CryptoAPIError(f"CoinGecko API returned HTTP error: {e}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Unexpected request error: {e}")
            raise CryptoAPIError("Unexpected API error")

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