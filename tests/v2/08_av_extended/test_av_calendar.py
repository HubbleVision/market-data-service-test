"""
AV 扩展 — 日历功能
覆盖: EARNINGS_CALENDAR, IPO_CALENDAR
"""
from framework import BaseTester, TestStatus


def test_av_earnings_calendar(tester: BaseTester) -> list:
    """盈利日历 EARNINGS_CALENDAR"""
    results = []

    for horizon in ["3month", "6month", "12month"]:
        resp = tester.client.v2_av_earnings_calendar(horizon=horizon)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or []
            ok = isinstance(items, list)

        results.append(tester._make_result(
            f"EARNINGS_CALENDAR (horizon={horizon})",
            "av_calendar",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"盈利日历 - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_ipo_calendar(tester: BaseTester) -> list:
    """IPO 日历 IPO_CALENDAR"""
    results = []
    resp = tester.client.v2_av_ipo_calendar()
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list)

    results.append(tester._make_result(
        "IPO_CALENDAR",
        "av_calendar",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"IPO日历 - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results
