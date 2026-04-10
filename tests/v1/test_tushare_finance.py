# V1 LEGACY - to be removed when V2 migration is complete
from framework import BaseTester, TestResult, TestStatus


def test_finance(tester: BaseTester) -> list:
    results = []
    ts_code = "000001.SZ"

    # 1. get_finance_income
    resp = tester.client.get_finance_income(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance income",
        "v1_finance_income",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_income - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. get_finance_balancesheet
    resp = tester.client.get_finance_balancesheet(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance balancesheet",
        "v1_finance_balancesheet",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_balancesheet - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. get_finance_cashflow
    resp = tester.client.get_finance_cashflow(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance cashflow",
        "v1_finance_cashflow",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_cashflow - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. get_finance_indicator
    resp = tester.client.get_finance_indicator(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance indicator",
        "v1_finance_indicator",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_indicator - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. get_finance_forecast
    resp = tester.client.get_finance_forecast(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance forecast",
        "v1_finance_forecast",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_forecast - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. get_finance_express
    resp = tester.client.get_finance_express(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance express",
        "v1_finance_express",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_express - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 7. get_finance_dividend
    resp = tester.client.get_finance_dividend(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance dividend",
        "v1_finance_dividend",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_dividend - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 8. get_finance_disclosure_date
    resp = tester.client.get_finance_disclosure_date(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance disclosure_date",
        "v1_finance_disclosure_date",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_disclosure_date - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 9. get_finance_main_bz
    resp = tester.client.get_finance_main_bz(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: finance main_bz",
        "v1_finance_main_bz",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"finance_main_bz - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
