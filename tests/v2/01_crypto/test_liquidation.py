"""
V2 Crypto Liquidation tests (8 endpoints)
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_liquidation(tester: BaseTester) -> list:
    """Test all V2 liquidation endpoints"""
    results = []

    endpoints = [
        ("realtime", lambda: tester.client.v2_get_liquidation_realtime(coin="BTC")),
        ("history", lambda: tester.client.v2_get_liquidation_history(
            symbol="BTCUSDT", interval="1h", end_time=_END_TIME, size=10)),
        ("agg-history", lambda: tester.client.v2_get_liquidation_agg_history(
            coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
        ("orders", lambda: tester.client.v2_get_liquidation_orders(
            coin="BTC", interval="1h", end_time=_END_TIME, size=10)),
        ("map", lambda: tester.client.v2_get_liquidation_map(coin="BTC")),
        ("heatmap", lambda: tester.client.v2_get_liquidation_heatmap(coin="BTC")),
        ("agg-map", lambda: tester.client.v2_get_liquidation_agg_map(coin="BTC", interval="1h")),
        ("heatmap-symbols", lambda: tester.client.v2_get_liquidation_heatmap_symbols()),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"Liquidation: {name}",
            "crypto_liquidation",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"liquidation/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
