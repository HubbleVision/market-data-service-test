"""
V2 Crypto ETF tests (4 endpoints)
"""
from framework import BaseTester, TestResult, TestStatus


def test_etf(tester: BaseTester) -> list:
    """Test all V2 ETF endpoints"""
    results = []

    endpoints = [
        ("btc", lambda: tester.client.v2_get_etf_btc()),
        ("eth", lambda: tester.client.v2_get_etf_eth()),
        ("btc-flow", lambda: tester.client.v2_get_etf_btc_flow()),
        ("eth-flow", lambda: tester.client.v2_get_etf_eth_flow()),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"ETF: {name}",
            "crypto_etf",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"etf/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
