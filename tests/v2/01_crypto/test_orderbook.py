"""
V2 Crypto Order Book & Order Flow tests (4 endpoints)
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_orderbook(tester: BaseTester) -> list:
    """Test all V2 order book and order flow endpoints"""
    results = []

    endpoints = [
        ("by-symbol", lambda: tester.client.v2_get_order_book_by_symbol(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            product_type="SWAP", rate="0.01", end_time=_END_TIME, size=10)),
        ("by-exchange", lambda: tester.client.v2_get_order_book_by_exchange(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            product_type="SWAP", rate="0.01", base_coin="BTC",
            end_time=_END_TIME, size=10)),
        ("heatmap", lambda: tester.client.v2_get_order_book_heatmap(
            symbol="BTCUSDT", exchange="Binance", interval="1m",
            end_time=_END_TIME, size=10)),
        ("order-flow-lists", lambda: tester.client.v2_get_order_flow_lists(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            product_type="SWAP", tick_count="2", end_time=_END_TIME, size=10)),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"OrderBook: {name}",
            "crypto_orderbook",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"order-book/order-flow/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
