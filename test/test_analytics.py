from crypto_sdk.analytics import biggest_gainer
from crypto_sdk.models import CryptoAsset


def test_biggest_gainer():
    assets = [
        CryptoAsset("btc", "btc", "Bitcoin", 100, 1_000_000, 2),
        CryptoAsset("eth", "eth", "Ethereum", 200, 1_000_000, 5),
        CryptoAsset("xrp", "xrp", "XRP", 50, 1_000_000, 1),
    ]

    result = biggest_gainer(assets)

    assert result.name == "Ethereum"
