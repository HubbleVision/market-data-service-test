"""
V2 CNStock macro tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_macro(tester: BaseTester) -> list:
    """Test V2 cnstock macro endpoints"""
    results = []

    # 1. v2_get_macro_shibor
    resp = tester.client.v2_get_macro_shibor(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: macro shibor",
        "cnstock_macro_shibor",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro shibor - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. v2_get_macro_lpr
    resp = tester.client.v2_get_macro_lpr(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: macro lpr",
        "cnstock_macro_lpr",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro lpr - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. v2_get_macro_cpi
    resp = tester.client.v2_get_macro_cpi(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: macro cpi",
        "cnstock_macro_cpi",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro cpi - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. v2_get_macro_ppi
    resp = tester.client.v2_get_macro_ppi(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: macro ppi",
        "cnstock_macro_ppi",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro ppi - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. v2_get_macro_gdp
    resp = tester.client.v2_get_macro_gdp(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: macro gdp",
        "cnstock_macro_gdp",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro gdp - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. v2_get_macro_money_supply
    resp = tester.client.v2_get_macro_money_supply(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: macro money supply",
        "cnstock_macro_money_supply",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro money supply - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
