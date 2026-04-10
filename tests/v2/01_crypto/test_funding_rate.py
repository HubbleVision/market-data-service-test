"""
V2 Crypto Funding Rate tests (7 endpoints)
Merged from original test_coinank_funding_rate.py
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_funding_rate(tester: BaseTester) -> list:
    """Test all V2 funding rate endpoints"""
    results = []

    endpoints = [
        ("realtime", lambda: tester.client.v2_get_funding_realtime(type_="current")),
        ("history", lambda: tester.client.v2_get_funding_history(
            exchange="Binance", symbol="BTCUSDT", interval="1h",
            end_time=_END_TIME, size=10)),
        ("cumulative", lambda: tester.client.v2_get_funding_cumulative(type_="day")),
        ("weighted", lambda: tester.client.v2_get_funding_weighted(
            base_coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
        ("kline", lambda: tester.client.v2_get_funding_kline(
            exchange="Binance", symbol="BTCUSDT", interval="1h",
            end_time=_END_TIME, size=10)),
        ("heatmap", lambda: tester.client.v2_get_funding_heatmap(
            type_="marketCap", interval="1M")),
        ("symbol-history", lambda: tester.client.v2_get_funding_symbol_history(
            exchange="Binance", symbol="BTCUSDT", interval="1h",
            end_time=_END_TIME, size=10)),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"FundingRate: {name}",
            "crypto_funding_rate",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"funding-rate/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
