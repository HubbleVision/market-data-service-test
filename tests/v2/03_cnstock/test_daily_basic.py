"""
V2 CNStock daily-basic and adj-factor tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_daily_basic(tester: BaseTester) -> list:
    """Test V2 cnstock daily-basic and adj-factor endpoints"""
    results = []

    # Daily basic
    resp = tester.client.v2_get_cnstock_daily_basic(ts_code="000001.SZ")
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("daily_basic") or data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "CNStock: daily-basic",
        "cnstock_daily_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"daily-basic(000001.SZ) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Adj factor
    resp = tester.client.v2_get_cnstock_adj_factor(ts_code="000001.SZ")
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("adj_factor") or data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "CNStock: adj-factor",
        "cnstock_daily_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"adj-factor(000001.SZ) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
