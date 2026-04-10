"""
V2 CNStock index tests
Basic, daily, weekly, monthly, daily-basic, weight
Note: index_classify removed - tushare data source unavailable
"""
from framework import BaseTester, TestResult, TestStatus

INDEX_ENDPOINTS = [
    ("basic", "index_basic", {}),
    ("daily", "index_daily", {"ts_code": "000001.SH"}),
    ("weekly", "index_weekly", {"ts_code": "000001.SH"}),
    ("monthly", "index_monthly", {"ts_code": "000001.SH"}),
    ("daily-basic", "index_daily_basic", {"ts_code": "000001.SH"}),
    ("weight", "index_weight", {"index_code": "000300.SH"}),
]


def test_cnstock_index(tester: BaseTester) -> list:
    """Test all 7 V2 cnstock index endpoints"""
    results = []

    for label, tag, params in INDEX_ENDPOINTS:
        method_name = f"v2_get_cnstock_index_{label.replace('-', '_')}"
        method = getattr(tester.client, method_name, None)
        if method is None:
            results.append(tester._make_result(
                f"CNStock: index-{label}",
                "cnstock_index",
                TestStatus.FAILED,
                f"index-{label}: method {method_name} not found",
                0,
                f"Method {method_name} does not exist on client",
            ))
            continue

        resp = method(**params)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}
        if ok:
            items = data.get("items") or data.get("indices") or data.get("data") or []
            if not isinstance(items, list) or len(items) == 0:
                ok = False

        results.append(tester._make_result(
            f"CNStock: index-{label}",
            "cnstock_index",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"index-{label} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
