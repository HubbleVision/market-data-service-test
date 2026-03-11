#!/usr/bin/env python3
"""
Quick test to verify service is running
"""
import requests
from config import BASE_URL, API_KEY

def test_service():
    """Test if the market data service is accessible"""
    # Test health endpoint
    response = requests.get(
        f"{BASE_URL}/api/v1/health",
        headers={"X-API-Key": API_KEY},
        timeout=10
    )
    print(f"Service URL: {BASE_URL}")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    # Test K-line endpoint
    response = requests.get(
        f"{BASE_URL}/api/v1/klines",
        params={
            "exchange": "binance",
            "symbol": "BTC/USDT",
            "interval": "1h",
            "limit": 10
        },
        headers={"X-API-Key": API_KEY},
        timeout=10
    )
    print(f"\nK-line test status: {response.status_code}")

    # Test indicator endpoint
    response = requests.post(
        f"{BASE_URL}/api/v1/indicators/technical",
        json={
            "exchange": "binance",
            "symbol": "BTC/USDT",
            "interval": "1h",
            "limit": 100,
            "indicators": [
                {"type": "sma", "params": [20]}
            ]
        },
        headers={"X-API-Key": API_KEY},
        timeout=10
    )
    print(f"\nIndicator test status: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    print("\n" + "="*50)
    print("Service is running and accessible!")

if __name__ == "__main__":
    test_service()
