"""
V2 Crypto Market Overview tests (price, marketcap, futures)
"""
from framework import BaseTester, TestResult, TestStatus


def test_market_overview(tester: BaseTester) -> list:
    """Test V2 crypto market overview endpoints"""
    results = []

    endpoints = [
        ("coins", lambda: tester.client.v2_get_crypto_coins()),
        ("price", lambda: tester.client.v2_get_crypto_price(symbol="BTCUSDT")),
        ("marketcap", lambda: tester.client.v2_get_crypto_marketcap(coin="BTC")),
        ("futures", lambda: tester.client.v2_get_crypto_futures()),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"MarketOverview: {name}",
            "crypto_market_overview",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
