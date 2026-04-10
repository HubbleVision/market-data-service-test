# V1 LEGACY - to be removed when V2 migration is complete
from framework import BaseTester, TestResult, TestStatus


def test_fund(tester: BaseTester) -> list:
    results = []
    ts_code = "000001.SZ"

    # 1. get_fund_basic
    resp = tester.client.get_fund_basic(market="E", limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund basic",
        "v1_fund_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_basic - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. get_fund_nav
    resp = tester.client.get_fund_nav(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund nav",
        "v1_fund_nav",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_nav - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. get_fund_daily
    resp = tester.client.get_fund_daily(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund daily",
        "v1_fund_daily",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_daily - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. get_fund_portfolio
    resp = tester.client.get_fund_portfolio(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund portfolio",
        "v1_fund_portfolio",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_portfolio - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. get_fund_etf_basic
    resp = tester.client.get_fund_etf_basic(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund etf_basic",
        "v1_fund_etf_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_etf_basic - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. get_fund_share
    resp = tester.client.get_fund_share(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund share",
        "v1_fund_share",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_share - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 7. get_fund_div
    resp = tester.client.get_fund_div(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund div",
        "v1_fund_div",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_div - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 8. get_fund_manager
    resp = tester.client.get_fund_manager(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund manager",
        "v1_fund_manager",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_manager - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 9. get_fund_company
    resp = tester.client.get_fund_company(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund company",
        "v1_fund_company",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_company - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 10. get_fund_etf_basic (duplicate call as specified in requirements)
    resp = tester.client.get_fund_etf_basic(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: fund etf_basic (duplicate)",
        "v1_fund_etf_basic_dup",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"fund_etf_basic (dup) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
