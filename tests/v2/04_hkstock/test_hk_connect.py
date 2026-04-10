"""
V2 HKStock Connect tests: ggt-top10, ggt-daily, hold
"""
from framework import BaseTester, TestResult, TestStatus


def test_hkstock_ggt_top10(tester: BaseTester) -> list:
    """Test V2 hkstock ggt-top10 endpoint"""
    results = []

    resp = tester.client.v2_get_hkstock_ggt_top10(trade_date="20260403")
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "HKStock: ggt-top10",
        "hkstock_ggt_top10",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"ggt-top10 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_hkstock_ggt_daily(tester: BaseTester) -> list:
    """Test V2 hkstock ggt-daily endpoint"""
    results = []

    resp = tester.client.v2_get_hkstock_ggt_daily()
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "HKStock: ggt-daily",
        "hkstock_ggt_daily",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"ggt-daily - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_hkstock_hold(tester: BaseTester) -> list:
    """Test V2 hkstock hold endpoint"""
    results = []

    resp = tester.client.v2_get_hkstock_hold()
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "HKStock: hold",
        "hkstock_hold",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"hold - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
