# V1 LEGACY - to be removed when V2 migration is complete
from framework import BaseTester, TestResult, TestStatus


def test_macro(tester: BaseTester) -> list:
    results = []

    # 1. get_macro_shibor
    resp = tester.client.get_macro_shibor(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: macro shibor",
        "v1_macro_shibor",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro_shibor - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. get_macro_lpr
    resp = tester.client.get_macro_lpr(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: macro lpr",
        "v1_macro_lpr",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro_lpr - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. get_macro_cpi
    resp = tester.client.get_macro_cpi(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: macro cpi",
        "v1_macro_cpi",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro_cpi - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. get_macro_ppi
    resp = tester.client.get_macro_ppi(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: macro ppi",
        "v1_macro_ppi",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro_ppi - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. get_macro_gdp
    resp = tester.client.get_macro_gdp(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: macro gdp",
        "v1_macro_gdp",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro_gdp - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. get_macro_money
    resp = tester.client.get_macro_money(limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: macro money",
        "v1_macro_money",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"macro_money - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
