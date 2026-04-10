"""
V2 Crypto RSI Screener & Proxy tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_crypto_misc(tester: BaseTester) -> list:
    """Test V2 crypto RSI screener and proxy endpoints"""
    results = []

    # RSI Screener
    resp = tester.client.v2_get_crypto_rsi_screener(interval="1H", exchange="Binance")
    ok = resp.success
    results.append(tester._make_result(
        "RSI Screener",
        "crypto_misc",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"rsi/screener - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
