"""
V2 Crypto Whale & Large Order tests (4 endpoints)
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_whale_large_order(tester: BaseTester) -> list:
    """Test V2 whale and large order endpoints"""
    results = []

    endpoints = [
        ("whale-positions", lambda: tester.client.v2_get_whale_positions(size="10")),
        ("whale-activity", lambda: tester.client.v2_get_whale_activity(size="10")),
        ("large-order-market", lambda: tester.client.v2_get_large_order_market(
            symbol="BTCUSDT", product_type="SWAP", amount="10000000",
            end_time=_END_TIME, size="10")),
        ("large-order-limit", lambda: tester.client.v2_get_large_order_limit(
            symbol="BTCUSDT", exchange_type="SWAP", is_history="true",
            amount="1000000", exchange="Binance", side="ask",
            start_time=_END_TIME, size="10")),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"Whale/LargeOrder: {name}",
            "crypto_whale_large_order",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
