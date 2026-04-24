"""
V2 Crypto Liquidation tests
爆仓数据相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus

TEST_SYMBOL = "BTC-USDT"
TEST_COIN = "BTC"
TEST_INTERVAL = "1h"


def test_crypto_liquidation_realtime(tester: BaseTester) -> list:
    """Test liquidation realtime endpoints"""
    results = []

    # Test without coin parameter
    resp = tester.client.v2_get_liquidation_realtime()
    ok = resp.success
    results.append(tester._make_result(
        "CryptoLiquidation: realtime",
        "crypto_liq_realtime",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"liq_realtime - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test with coin parameter
    resp2 = tester.client.v2_get_liquidation_realtime(coin=TEST_COIN)
    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoLiquidation: realtime_with_coin",
        "crypto_liq_realtime_coin",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"liq_realtime_with_coin - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results


def test_crypto_liquidation_history(tester: BaseTester) -> list:
    """Test liquidation history endpoints"""
    results = []

    endpoints = [
        ("liq_agg_history", lambda: tester.client.v2_get_liquidation_agg_history(
            coin=TEST_COIN, interval=TEST_INTERVAL, size=100)),
        ("liq_history", lambda: tester.client.v2_get_liquidation_history(
            symbol=TEST_SYMBOL, interval=TEST_INTERVAL, size=100)),
        ("liq_orders", lambda: tester.client.v2_get_liquidation_orders(
            coin=TEST_COIN, interval=TEST_INTERVAL, size=100)),
    ]

    for label, method in endpoints:
        try:
            resp = method()
            ok = resp.success
            results.append(tester._make_result(
                f"CryptoLiquidation: {label}",
                f"crypto_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"CryptoLiquidation: {label}",
                f"crypto_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results


def test_crypto_liquidation_heatmap(tester: BaseTester) -> list:
    """Test liquidation heatmap endpoints"""
    results = []

    endpoints = [
        ("liq_map", lambda: tester.client.v2_get_liquidation_map(coin=TEST_COIN)),
        ("liq_heatmap", lambda: tester.client.v2_get_liquidation_heatmap(coin=TEST_COIN)),
        ("liq_agg_map", lambda: tester.client.v2_get_liquidation_agg_map(
            coin=TEST_COIN, interval=TEST_INTERVAL)),
        ("liq_heatmap_symbols", lambda: tester.client.v2_get_liquidation_heatmap_symbols()),
    ]

    for label, method in endpoints:
        try:
            resp = method()
            ok = resp.success
            results.append(tester._make_result(
                f"CryptoLiquidation: {label}",
                f"crypto_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"CryptoLiquidation: {label}",
                f"crypto_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results
