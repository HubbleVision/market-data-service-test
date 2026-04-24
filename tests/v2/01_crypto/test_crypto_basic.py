"""
V2 Crypto Basic tests
Klines, exchanges, symbols list
"""
from framework import BaseTester, TestResult, TestStatus

# Test parameters
TEST_EXCHANGE = "binance"
TEST_SYMBOL = "BTC-USDT"
TEST_INTERVAL = "1h"

BASIC_ENDPOINTS = [
    ("exchanges", "v2_get_exchanges", {}),
    ("symbols_list", "v2_get_symbols_list", {"exchange": TEST_EXCHANGE}),
]


def test_crypto_basic(tester: BaseTester) -> list:
    """Test V2 crypto basic endpoints: exchanges, symbols list"""
    results = []

    for label, method_name, params in BASIC_ENDPOINTS:
        method = getattr(tester.client, method_name, None)
        if method is None:
            results.append(tester._make_result(
                f"CryptoBasic: {label}",
                "crypto_basic",
                TestStatus.FAILED,
                f"{label}: method {method_name} not found",
                0,
                f"Method {method_name} does not exist on client",
            ))
            continue

        resp = method(**params)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}
        if ok:
            items = data.get("items") or data.get("data") or []
            if not isinstance(items, list):
                ok = False

        results.append(tester._make_result(
            f"CryptoBasic: {label}",
            "crypto_basic",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{label} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_crypto_klines(tester: BaseTester) -> list:
    """Test V2 crypto klines endpoint with various parameters"""
    results = []

    # Test basic kline request
    resp = tester.client.v2_get_kline(
        exchange=TEST_EXCHANGE,
        symbol=TEST_SYMBOL,
        interval=TEST_INTERVAL,
        limit=100
    )

    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "CryptoBasic: klines",
        "crypto_klines",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"klines - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test kline with time range
    resp2 = tester.client.v2_get_kline(
        exchange=TEST_EXCHANGE,
        symbol=TEST_SYMBOL,
        interval=TEST_INTERVAL,
        start_time="2024-01-01T00:00:00Z",
        end_time="2024-01-02T00:00:00Z"
    )

    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoBasic: klines_with_range",
        "crypto_klines_range",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"klines_with_range - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results
