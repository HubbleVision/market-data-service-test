"""
V2 Crypto CVD & Buy/Sell tests (7 endpoints)
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_cvd_buy_sell(tester: BaseTester) -> list:
    """Test all V2 CVD and buy/sell endpoints"""
    results = []

    endpoints = [
        ("cvd-kline", lambda: tester.client.v2_get_cvd_kline(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            product_type="SWAP", end_time=_END_TIME, size=10)),
        ("buy-sell-count", lambda: tester.client.v2_get_buy_sell_count(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            product_type="SWAP", end_time=_END_TIME, size=10)),
        ("buy-sell-volume", lambda: tester.client.v2_get_buy_sell_volume(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            product_type="SWAP", end_time=_END_TIME, size=10)),
        ("buy-sell-amount", lambda: tester.client.v2_get_buy_sell_amount(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            product_type="SWAP", end_time=_END_TIME, size=10)),
        ("buy-sell-agg-count", lambda: tester.client.v2_get_buy_sell_agg_count(
            base_coin="BTC", interval="1h", product_type="SWAP",
            end_time=_END_TIME, size=10)),
        ("buy-sell-agg-volume", lambda: tester.client.v2_get_buy_sell_agg_volume(
            base_coin="BTC", interval="1h", product_type="SWAP",
            end_time=_END_TIME, size=10)),
        ("buy-sell-agg-amount", lambda: tester.client.v2_get_buy_sell_agg_amount(
            base_coin="BTC", interval="1h", product_type="SWAP",
            end_time=_END_TIME, size=10)),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"CVD/BuySell: {name}",
            "crypto_cvd_buy_sell",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
