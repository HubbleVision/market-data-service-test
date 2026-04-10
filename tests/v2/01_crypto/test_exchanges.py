"""
V2 Crypto exchanges and symbols tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_v2_exchanges(tester: BaseTester) -> list:
    """Test V2 exchange and symbol list endpoints"""
    results = []

    # Test exchanges list
    resp = tester.client.v2_get_exchanges()
    ok = resp.success
    results.append(tester._make_result(
        "V2 Exchanges: list",
        "crypto_exchanges",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"GET /crypto/exchanges - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test symbols list
    resp = tester.client.v2_get_symbols_list(exchange="Binance")
    ok = resp.success
    results.append(tester._make_result(
        "V2 Symbols: Binance list",
        "crypto_exchanges",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"GET /crypto/symbols/list - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
