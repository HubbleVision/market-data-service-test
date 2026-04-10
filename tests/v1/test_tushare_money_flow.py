# V1 LEGACY - to be removed when V2 migration is complete
from framework import BaseTester, TestResult, TestStatus


def test_money_flow(tester: BaseTester) -> list:
    results = []
    ts_code = "000001.SZ"

    # 1. get_moneyflow_hsgt
    resp = tester.client.get_moneyflow_hsgt(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: moneyflow hsgt",
        "v1_moneyflow_hsgt",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow_hsgt - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. get_moneyflow_hsgt_top10
    resp = tester.client.get_moneyflow_hsgt_top10(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: moneyflow hsgt_top10",
        "v1_moneyflow_hsgt_top10",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow_hsgt_top10 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. get_moneyflow_margin
    resp = tester.client.get_moneyflow_margin(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: moneyflow margin",
        "v1_moneyflow_margin",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow_margin - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. get_moneyflow_margin_detail
    resp = tester.client.get_moneyflow_margin_detail(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: moneyflow margin_detail",
        "v1_moneyflow_margin_detail",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow_margin_detail - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. get_moneyflow_stock
    resp = tester.client.get_moneyflow_stock(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: moneyflow stock",
        "v1_moneyflow_stock",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"moneyflow_stock - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
