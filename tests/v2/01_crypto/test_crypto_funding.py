"""
V2 Crypto Funding Rate tests
资金费率相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus

TEST_EXCHANGE = "binance"
TEST_SYMBOL = "BTC-USDT"
TEST_BASE_COIN = "BTC"
TEST_INTERVAL = "1h"


def test_crypto_funding_realtime(tester: BaseTester) -> list:
    """Test funding rate realtime endpoints"""
    results = []

    # Test without type
    resp = tester.client.v2_get_funding_realtime()
    ok = resp.success
    results.append(tester._make_result(
        "CryptoFunding: realtime",
        "crypto_funding_realtime",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"funding_realtime - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test with type
    resp2 = tester.client.v2_get_funding_realtime(type_=" perpetual")
    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoFunding: realtime_with_type",
        "crypto_funding_realtime_type",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"funding_realtime_with_type - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results


def test_crypto_funding_history(tester: BaseTester) -> list:
    """Test funding rate history endpoints"""
    results = []

    endpoints = [
        ("funding_history", lambda: tester.client.v2_get_funding_history(
            exchange=TEST_EXCHANGE, symbol=TEST_SYMBOL, interval=TEST_INTERVAL, size=100)),
        ("funding_kline", lambda: tester.client.v2_get_funding_kline(
            exchange=TEST_EXCHANGE, symbol=TEST_SYMBOL, interval=TEST_INTERVAL, size=100)),
        ("funding_symbol_history", lambda: tester.client.v2_get_funding_symbol_history(
            exchange=TEST_EXCHANGE, symbol=TEST_SYMBOL, interval=TEST_INTERVAL, size=100)),
    ]

    for label, method in endpoints:
        try:
            resp = method()
            ok = resp.success
            results.append(tester._make_result(
                f"CryptoFunding: {label}",
                f"crypto_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"CryptoFunding: {label}",
                f"crypto_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results


def test_crypto_funding_aggregated(tester: BaseTester) -> list:
    """Test aggregated funding rate endpoints"""
    results = []

    # Test cumulative funding
    resp = tester.client.v2_get_funding_cumulative()
    ok = resp.success
    results.append(tester._make_result(
        "CryptoFunding: cumulative",
        "crypto_funding_cumulative",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"funding_cumulative - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test weighted funding
    resp2 = tester.client.v2_get_funding_weighted(
        base_coin=TEST_BASE_COIN, interval=TEST_INTERVAL, size=100)
    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoFunding: weighted",
        "crypto_funding_weighted",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"funding_weighted - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    # Test funding heatmap
    resp3 = tester.client.v2_get_funding_heatmap(type_="coin", interval="1d")
    ok3 = resp3.success
    results.append(tester._make_result(
        "CryptoFunding: heatmap",
        "crypto_funding_heatmap",
        TestStatus.PASSED if ok3 else TestStatus.FAILED,
        f"funding_heatmap - {'OK' if ok3 else 'FAILED'}",
        resp3.response_time_ms,
        resp3.error if not ok3 else None,
    ))

    return results
