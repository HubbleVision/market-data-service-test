"""
V2 CNStock symbols tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_symbols(tester: BaseTester) -> list:
    """Test V2 cnstock symbols endpoint"""
    results = []

    resp = tester.client.v2_get_cnstock_symbols(list_status="L")
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        total = data.get("total", 0)
        items = data.get("symbols") or data.get("items") or []
        if not isinstance(total, int) or total <= 0:
            ok = False
        elif not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "CNStock: symbols",
        "cnstock_symbols",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbols(list_status=L) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
