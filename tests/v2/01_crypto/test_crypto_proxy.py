"""
V2 Crypto Proxy endpoint test
"""
from framework import BaseTester, TestResult, TestStatus


def test_crypto_proxy(tester: BaseTester) -> list:
    """Test V2 crypto proxy endpoint"""
    results = []

    # Test proxy with a simple CoinAnk endpoint path
    resp = tester.client.v2_get_crypto_proxy("open-interest/list", baseCoin="BTC")
    ok = resp.success
    results.append(tester._make_result(
        "Proxy: open-interest/list",
        "crypto_proxy",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"proxy/open-interest/list - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
