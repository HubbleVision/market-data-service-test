"""
V2 HKStock basic tests: symbols, daily K-line, trade calendar
"""
from config import TUSHARE_CONFIG
from framework import BaseTester, TestResult, TestStatus

HK_SYMBOLS = TUSHARE_CONFIG["hkstock"]["symbols"]


def test_hkstock_symbols(tester: BaseTester) -> list:
    """Test V2 hkstock symbols endpoint"""
    results = []

    resp = tester.client.v2_get_hkstock_symbols(list_status="L")
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
        "HKStock: symbols",
        "hkstock_symbols",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbols(list_status=L) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_hkstock_daily(tester: BaseTester) -> list:
    """Test V2 hkstock daily K-line endpoint"""
    results = []

    for symbol in HK_SYMBOLS:
        resp = tester.client.v2_get_hkstock_daily(symbol=symbol)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}
        if ok:
            items = data.get("klines") or data.get("items") or data.get("data") or []
            if not isinstance(items, list) or len(items) == 0:
                ok = False

        results.append(tester._make_result(
            f"HKStock: daily ({symbol})",
            "hkstock_daily",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"daily({symbol}) - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_hkstock_trade_cal(tester: BaseTester) -> list:
    """Test V2 hkstock trade calendar endpoint"""
    results = []

    resp = tester.client.v2_get_hkstock_trade_cal()
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("tradeCal") or data.get("items") or data.get("data") or []
        if not isinstance(items, list) or len(items) == 0:
            ok = False

    results.append(tester._make_result(
        "HKStock: trade-cal",
        "hkstock_trade_cal",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"trade-cal - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
