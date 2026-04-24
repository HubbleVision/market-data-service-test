"""
V2 Crypto Open Interest tests
持仓量相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus

TEST_EXCHANGE = "binance"
TEST_SYMBOL = "BTC-USDT"
TEST_BASE_COIN = "BTC"
TEST_INTERVAL = "1h"


def test_crypto_oi_list(tester: BaseTester) -> list:
    """Test open interest list endpoint"""
    results = []

    # Test without parameters
    resp = tester.client.v2_get_oi_list()
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("items") or data.get("data") or []
        if not isinstance(items, list):
            ok = False

    results.append(tester._make_result(
        "CryptoOI: list",
        "crypto_oi_list",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"oi_list - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test with base_coin parameter
    resp2 = tester.client.v2_get_oi_list(base_coin=TEST_BASE_COIN)
    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoOI: list_with_coin",
        "crypto_oi_list_coin",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"oi_list_with_coin - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results


def test_crypto_oi_history(tester: BaseTester) -> list:
    """Test open interest history endpoints"""
    results = []

    endpoints = [
        ("oi_history", lambda: tester.client.v2_get_oi_history(
            exchange=TEST_EXCHANGE, symbol=TEST_SYMBOL, interval=TEST_INTERVAL, size=100)),
        ("oi_kline", lambda: tester.client.v2_get_oi_kline(
            exchange=TEST_EXCHANGE, symbol=TEST_SYMBOL, interval=TEST_INTERVAL, size=100)),
        ("oi_agg_history", lambda: tester.client.v2_get_oi_agg_history(
            base_coin=TEST_BASE_COIN, interval=TEST_INTERVAL, size=100)),
        ("oi_agg_kline", lambda: tester.client.v2_get_oi_agg_kline(
            base_coin=TEST_BASE_COIN, interval=TEST_INTERVAL, size=100)),
    ]

    for label, method in endpoints:
        try:
            resp = method()
            ok = resp.success
            results.append(tester._make_result(
                f"CryptoOI: {label}",
                f"crypto_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"CryptoOI: {label}",
                f"crypto_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results


def test_crypto_oi_realtime(tester: BaseTester) -> list:
    """Test open interest realtime endpoints"""
    results = []

    # Test coin realtime
    resp = tester.client.v2_get_oi_coin_realtime(base_coin=TEST_BASE_COIN)
    ok = resp.success
    results.append(tester._make_result(
        "CryptoOI: coin_realtime",
        "crypto_oi_coin_realtime",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"oi_coin_realtime - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test OI vs market cap
    resp2 = tester.client.v2_get_oi_vs_mc(
        base_coin=TEST_BASE_COIN, interval=TEST_INTERVAL, size=100)
    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoOI: oi_vs_mc",
        "crypto_oi_vs_mc",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"oi_vs_mc - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results
