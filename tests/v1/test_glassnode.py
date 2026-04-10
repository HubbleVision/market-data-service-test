# V1 LEGACY - to be removed when V2 migration is complete
from framework import BaseTester, TestResult, TestStatus


def test_glassnode(tester: BaseTester) -> list:
    results = []

    endpoints = [
        ("btc/supply", {"a": "BTC"}),
        ("btc/marketcap", {"a": "BTC"}),
        ("btc/nvt", {"a": "BTC"}),
    ]

    for endpoint, params in endpoints:
        resp = tester.client.get_glassnode_data(endpoint, params)
        ok = resp.success
        results.append(tester._make_result(
            f"V1: glassnode/{endpoint}",
            f"v1_glassnode_{endpoint.replace('/', '_')}",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"glassnode/{endpoint} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
