"""
V2 CNStock company tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_company(tester: BaseTester) -> list:
    """Test V2 cnstock company endpoint"""
    results = []

    resp = tester.client.v2_get_cnstock_company(limit=10)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("companies") or data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "CNStock: company",
        "cnstock_company",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"company(limit=10) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
