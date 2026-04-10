"""
V2 CNStock K-line tests
Daily, weekly, monthly K-lines for 000001.SZ
"""
from framework import BaseTester, TestResult, TestStatus

CN_KLINE_PERIODS = ["daily", "weekly", "monthly"]


def test_cnstock_klines(tester: BaseTester) -> list:
    """Test V2 cnstock K-line endpoint across periods"""
    results = []

    for period in CN_KLINE_PERIODS:
        resp = tester.client.v2_get_cnstock_klines(
            symbol="000001.SZ", interval=period
        )
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}
        if ok:
            items = data.get("klines") or data.get("items") or data.get("data") or []
            if not isinstance(items, list) or len(items) == 0:
                ok = False

        results.append(tester._make_result(
            f"CNStock: klines ({period})",
            "cnstock_klines",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"klines(000001.SZ, {period}) - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
