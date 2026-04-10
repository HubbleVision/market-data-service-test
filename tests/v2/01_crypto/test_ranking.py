"""
V2 Crypto Ranking tests (4 endpoints)
"""
from framework import BaseTester, TestResult, TestStatus


def test_ranking(tester: BaseTester) -> list:
    """Test all V2 ranking endpoints"""
    results = []

    endpoints = [
        ("open-interest", lambda: tester.client.v2_get_ranking_open_interest()),
        ("volume", lambda: tester.client.v2_get_ranking_volume()),
        ("price-change", lambda: tester.client.v2_get_ranking_price_change()),
        ("liquidation", lambda: tester.client.v2_get_ranking_liquidation()),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"Ranking: {name}",
            "crypto_ranking",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"ranking/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
