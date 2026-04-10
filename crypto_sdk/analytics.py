# crypto_sdk/analytics.py


def top_movers(assets, threshold=5.0):
    return [
        asset for asset in assets if abs(asset.price_change_percentage_24h) > threshold
    ]


def average_price(assets):
    if not assets:
        return 0

    total = sum(asset.current_price for asset in assets)
    return total / len(assets)


def filter_by_market_cap(assets, min_market_cap):
    return [asset for asset in assets if asset.market_cap >= min_market_cap]


def biggest_gainer(assets):
    if not assets:
        return None

    return max(assets, key=lambda asset: asset.price_change_percentage_24h)
