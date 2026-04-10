"""
V2 CNStock money flow tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_moneyflow(tester: BaseTester) -> list:
    """Test V2 cnstock money flow endpoints"""
    results = []
    ts_code = "000001.SZ"

    # 1. v2_get_moneyflow_hsgt
    resp = tester.client.v2_get_moneyflow_hsgt(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: moneyflow hsgt",
        "cnstock_moneyflow_hsgt",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow hsgt - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. v2_get_moneyflow_hsgt_top10
    resp = tester.client.v2_get_moneyflow_hsgt_top10(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: moneyflow hsgt top10",
        "cnstock_moneyflow_hsgt_top10",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow hsgt top10 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. v2_get_moneyflow_margin
    resp = tester.client.v2_get_moneyflow_margin(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: moneyflow margin",
        "cnstock_moneyflow_margin",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow margin - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. v2_get_moneyflow_margin_detail
    resp = tester.client.v2_get_moneyflow_margin_detail(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: moneyflow margin detail",
        "cnstock_moneyflow_margin_detail",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow margin detail - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. v2_get_moneyflow_stock
    resp = tester.client.v2_get_moneyflow_stock(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: moneyflow stock",
        "cnstock_moneyflow_stock",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow stock - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
