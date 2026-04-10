"""
V2 CNStock misc tests
Name-change, new-share, stk-limit, suspend
"""
from framework import BaseTester, TestResult, TestStatus

MISC_ENDPOINTS = [
    ("name_change", "v2_get_cnstock_name_change", {"ts_code": "000001.SZ"}),
    ("new_share", "v2_get_cnstock_new_share", {}),
    ("stk_limit", "v2_get_cnstock_stk_limit", {"ts_code": "000001.SZ"}),
    ("suspend", "v2_get_cnstock_suspend", {"ts_code": "000001.SZ"}),
]


def test_cnstock_misc(tester: BaseTester) -> list:
    """Test V2 cnstock misc endpoints: name-change, new-share, stk-limit, suspend"""
    results = []

    for label, method_name, params in MISC_ENDPOINTS:
        method = getattr(tester.client, method_name, None)
        if method is None:
            results.append(tester._make_result(
                f"CNStock: {label}",
                "cnstock_misc",
                TestStatus.FAILED,
                f"{label}: method {method_name} not found",
                0,
                f"Method {method_name} does not exist on client",
            ))
            continue

        resp = method(**params)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}
        if ok:
            items = data.get("items") or data.get("data") or []
            if not isinstance(items, list) or len(items) == 0:
                ok = False

        results.append(tester._make_result(
            f"CNStock: {label}",
            "cnstock_misc",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{label} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
