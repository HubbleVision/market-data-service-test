"""
V2 CNStock trade calendar tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_trade_cal(tester: BaseTester) -> list:
    """Test V2 cnstock trade calendar endpoint"""
    results = []

    resp = tester.client.v2_get_cnstock_trade_cal(exchange="SSE")
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("cal") or data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "CNStock: trade-cal",
        "cnstock_trade_cal",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"trade-cal(exchange=SSE) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
