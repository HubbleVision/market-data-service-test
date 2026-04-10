"""
V2 Crypto Long/Short Ratio tests (7 endpoints)
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_long_short(tester: BaseTester) -> list:
    """Test all V2 long/short ratio endpoints"""
    results = []

    endpoints = [
        ("exchange", lambda: tester.client.v2_get_long_short_exchange(
            base_coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
        ("account", lambda: tester.client.v2_get_long_short_account(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            end_time=_END_TIME, size=10)),
        ("top-trader", lambda: tester.client.v2_get_long_short_top_trader(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            end_time=_END_TIME, size=10)),
        ("kline", lambda: tester.client.v2_get_long_short_kline(
            type_="longShortPerson", symbol="BTCUSDT", exchange="Binance",
            interval="1h", end_time=_END_TIME, size=10)),
        ("taker-ratio", lambda: tester.client.v2_get_long_short_taker_ratio(
            base_coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
        ("top-trader-account", lambda: tester.client.v2_get_long_short_top_trader_account(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            end_time=_END_TIME, size=10)),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"LongShort: {name}",
            "crypto_long_short",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"long-short/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
