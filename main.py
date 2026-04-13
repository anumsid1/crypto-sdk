# main.py

import argparse
from crypto_sdk.client import CoinGeckoClient
from crypto_sdk.analytics import top_movers, average_price, biggest_gainer, filter_by_market_cap


def parse_args():
    parser = argparse.ArgumentParser(
        description="Crypto SDK — fetch and analyse live market data"
    )

    parser.add_argument(
        "--currency",
        type=str,
        default=None,
        help="Currency to fetch prices in (default: from .env or usd)",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of coins to fetch (default: from .env or 10)",
    )

    parser.add_argument(
        "--top-movers",
        action="store_true",
        help="Show coins with >5%% price change in last 24h",
    )

    parser.add_argument(
        "--biggest-gainer",
        action="store_true",
        help="Show the single biggest gainer in the last 24h",
    )

    parser.add_argument(
        "--min-market-cap",
        type=float,
        default=None,
        help="Filter coins by minimum market cap (e.g. 1000000000 for $1B)",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    client = CoinGeckoClient()
    assets = client.fetch_market_data(vs_currency=args.currency, per_page=args.limit)

    print(f"\n=== Top {len(assets)} Coins ({(args.currency or 'usd').upper()}) ===")
    for asset in assets:
        print(f"  {asset.name:<20} ${asset.current_price:>12,.2f}  ({asset.price_change_percentage_24h:+.2f}%)")

    if args.top_movers:
        movers = top_movers(assets, threshold=5.0)
        print(f"\n=== Top Movers (>5% in 24h) ===")
        if movers:
            for asset in movers:
                print(f"  {asset.name:<20} {asset.price_change_percentage_24h:+.2f}%")
        else:
            print("  No coins moved more than 5% in the last 24h")

    if args.biggest_gainer:
        gainer = biggest_gainer(assets)
        if gainer:
            print(f"\n=== Biggest Gainer ===")
            print(f"  {gainer.name} at {gainer.price_change_percentage_24h:+.2f}%")

    if args.min_market_cap:
        filtered = filter_by_market_cap(assets, args.min_market_cap)
        print(f"\n=== Coins with Market Cap > ${args.min_market_cap:,.0f} ===")
        for asset in filtered:
            print(f"  {asset.name:<20} ${asset.market_cap:>20,.0f}")

    avg = average_price(assets)
    print(f"\n  Average price: ${avg:,.2f}")


if __name__ == "__main__":
    main()
