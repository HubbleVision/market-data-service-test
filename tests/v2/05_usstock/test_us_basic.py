"""
V2 USStock basic tests: symbols, daily K-line, trade calendar
"""
from config import TUSHARE_CONFIG
from framework import BaseTester, TestResult, TestStatus

US_SYMBOLS = TUSHARE_CONFIG["usstock"]["symbols"]


def test_usstock_symbols(tester: BaseTester) -> list:
    """Test V2 usstock symbols endpoint"""
    results = []

    resp = tester.client.v2_get_usstock_symbols()
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        total = data.get("total", 0)
        items = data.get("symbols") or data.get("items") or []
        if not isinstance(total, int) or total <= 0:
            ok = False
        elif not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "USStock: symbols",
        "usstock_symbols",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbols - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_usstock_daily(tester: BaseTester) -> list:
    """Test V2 usstock daily K-line endpoint"""
    results = []

    for symbol in US_SYMBOLS:
        resp = tester.client.v2_get_usstock_daily(symbol=symbol)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}
        if ok:
            items = data.get("klines") or data.get("items") or data.get("data") or []
            if not isinstance(items, list) or len(items) == 0:
                ok = False

        results.append(tester._make_result(
            f"USStock: daily ({symbol})",
            "usstock_daily",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"daily({symbol}) - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_usstock_trade_cal(tester: BaseTester) -> list:
    """Test V2 usstock trade calendar endpoint"""
    results = []

    resp = tester.client.v2_get_usstock_trade_cal()
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("tradeCal") or data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "USStock: trade-cal",
        "usstock_trade_cal",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"trade-cal - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
