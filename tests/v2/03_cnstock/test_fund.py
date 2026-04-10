"""
V2 CNStock fund tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_fund(tester: BaseTester) -> list:
    """Test V2 fund endpoints"""
    results = []
    ts_code = "000001.SZ"

    # 1. v2_get_fund_basic
    resp = tester.client.v2_get_fund_basic(market="E", limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund basic",
        "cnstock_fund_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund basic - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. v2_get_fund_nav
    resp = tester.client.v2_get_fund_nav(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund nav",
        "cnstock_fund_nav",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund nav - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. v2_get_fund_daily
    resp = tester.client.v2_get_fund_daily(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund daily",
        "cnstock_fund_daily",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund daily - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. v2_get_fund_portfolio
    resp = tester.client.v2_get_fund_portfolio(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund portfolio",
        "cnstock_fund_portfolio",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund portfolio - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. v2_get_fund_etf_basic
    resp = tester.client.v2_get_fund_etf_basic(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund etf basic",
        "cnstock_fund_etf_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund etf basic - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. v2_get_fund_share
    resp = tester.client.v2_get_fund_share(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund share",
        "cnstock_fund_share",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund share - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 7. v2_get_fund_div
    resp = tester.client.v2_get_fund_div(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund div",
        "cnstock_fund_div",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund div - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 8. v2_get_fund_manager
    resp = tester.client.v2_get_fund_manager(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund manager",
        "cnstock_fund_manager",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund manager - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 9. v2_get_fund_company
    resp = tester.client.v2_get_fund_company(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: fund company",
        "cnstock_fund_company",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund company - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
