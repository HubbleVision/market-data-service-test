"""
V2 Crypto Open Interest tests (7 endpoints)
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_open_interest(tester: BaseTester) -> list:
    """Test all V2 open interest endpoints"""
    results = []

    endpoints = [
        ("list", lambda: tester.client.v2_get_oi_list(base_coin="BTC")),
        ("history", lambda: tester.client.v2_get_oi_history(
            exchange="Binance", symbol="BTCUSDT", interval="1h",
            end_time=_END_TIME, size=10)),
        ("kline", lambda: tester.client.v2_get_oi_kline(
            exchange="Binance", symbol="BTCUSDT", interval="1h",
            end_time=_END_TIME, size=10)),
        ("agg-history", lambda: tester.client.v2_get_oi_agg_history(
            base_coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
        ("agg-kline", lambda: tester.client.v2_get_oi_agg_kline(
            base_coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
        ("coin-realtime", lambda: tester.client.v2_get_oi_coin_realtime(base_coin="BTC")),
        ("oi-vs-mc", lambda: tester.client.v2_get_oi_vs_mc(
            base_coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"OpenInterest: {name}",
            "crypto_open_interest",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"oi/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
