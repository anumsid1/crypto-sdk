import httpx
from .models import CryptoAsset


class AsyncCoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    async def fetch_market_data(self, vs_currency="usd"):
        url = f"{self.BASE_URL}/coins/markets"

        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": False
        }

        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

        data = response.json()

        return [
            CryptoAsset(
                id=item["id"],
                symbol=item["symbol"],
                name=item["name"],
                current_price=item["current_price"],
                market_cap=item["market_cap"],
                price_change_percentage_24h=item["price_change_percentage_24h"]
            )
            for item in data
        ]