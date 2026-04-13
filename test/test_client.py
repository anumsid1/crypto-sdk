import pytest
from unittest.mock import patch
import requests
from crypto_sdk.client import CoinGeckoClient, CryptoAPIError


def test_connection_error_raises_crypto_api_error():
    client = CoinGeckoClient(base_url="https://wrong-url.com")
    with patch.object(client.session, "get", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(CryptoAPIError, match="Failed to connect to CoinGecko API"):
            client.fetch_market_data()


def test_timeout_raises_crypto_api_error():
    client = CoinGeckoClient()
    with patch.object(client.session, "get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(CryptoAPIError, match="timed out"):
            client.fetch_market_data()


def test_http_error_raises_crypto_api_error():
    client = CoinGeckoClient()
    mock_response = requests.models.Response()
    mock_response.status_code = 500
    with patch.object(client.session, "get", side_effect=requests.exceptions.HTTPError("500 Server Error")):
        with pytest.raises(CryptoAPIError, match="HTTP error"):
            client.fetch_market_data()