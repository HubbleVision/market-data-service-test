"""
V2 CNStock finance tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_finance(tester: BaseTester) -> list:
    """Test V2 cnstock finance endpoints"""
    results = []
    ts_code = "000001.SZ"

    # 1. v2_get_finance_income
    resp = tester.client.v2_get_finance_income(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance income",
        "cnstock_finance_income",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance income - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. v2_get_finance_balancesheet
    resp = tester.client.v2_get_finance_balancesheet(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance balancesheet",
        "cnstock_finance_balancesheet",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance balancesheet - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. v2_get_finance_cashflow
    resp = tester.client.v2_get_finance_cashflow(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance cashflow",
        "cnstock_finance_cashflow",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance cashflow - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. v2_get_finance_indicator
    resp = tester.client.v2_get_finance_indicator(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance indicator",
        "cnstock_finance_indicator",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance indicator - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. v2_get_finance_forecast
    resp = tester.client.v2_get_finance_forecast(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance forecast",
        "cnstock_finance_forecast",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance forecast - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. v2_get_finance_express
    resp = tester.client.v2_get_finance_express(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance express",
        "cnstock_finance_express",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance express - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 7. v2_get_finance_dividend
    resp = tester.client.v2_get_finance_dividend(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance dividend",
        "cnstock_finance_dividend",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance dividend - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 8. v2_get_finance_disclosure_date
    resp = tester.client.v2_get_finance_disclosure_date(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance disclosure date",
        "cnstock_finance_disclosure_date",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance disclosure date - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 9. v2_get_finance_main_bz
    resp = tester.client.v2_get_finance_main_bz(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: finance main biz",
        "cnstock_finance_main_bz",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance main biz - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
