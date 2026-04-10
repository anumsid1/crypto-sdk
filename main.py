# main.py

from crypto_sdk.client import CoinGeckoClient
from crypto_sdk.analytics import top_movers, average_price


def main():
    client = CoinGeckoClient()

    assets = client.fetch_market_data()

    print("\n=== All Assets ===")
    for asset in assets:
        print(f"{asset.name}: ${asset.current_price}")

    movers = top_movers(assets, threshold=3.0)

    print("\n=== Top Movers (>3%) ===")
    for asset in movers:
        print(f"{asset.name}: {asset.price_change_percentage_24h}%")

    avg = average_price(assets)
    print(f"\nAverage Price of Top 10: ${avg:.2f}")


if __name__ == "__main__":
    main()