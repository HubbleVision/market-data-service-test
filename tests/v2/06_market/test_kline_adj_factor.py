"""
K线数据 adj_factor 字段移除验证 (V2)
覆盖: 三市场 (CN/HK/US) K线数据确认不包含 adj_factor 字段
V2 endpoints: /api/v2/cnstock/stocks, /api/v2/hkstock/stocks, /api/v2/usstock/stocks
"""
from framework import BaseTester, TestStatus


def test_kline_adj_factor(tester: BaseTester) -> list:
    """验证 V2 K线数据不包含 adj_factor 字段"""
    results = []

    cases = [
        ("CN", "000001.SZ", "cnstock", "A股 日K"),
        ("CN", "600519.SH", "cnstock", "A股 日K (SH)"),
        ("HK", "00700.HK", "hkstock", "港股 日K"),
        ("US", "AAPL", "usstock", "美股 日K"),
    ]

    for label, symbol, market, display in cases:
        name = f"adj_factor移除: {label} - {display} ({symbol})"
        if market == "cnstock":
            resp = tester.client.v2_get_cnstock_klines(symbol=symbol, limit=5)
        elif market == "hkstock":
            resp = tester.client.v2_get_hkstock_daily(symbol=symbol, limit=5)
        else:
            resp = tester.client.v2_get_usstock_daily(symbol=symbol, limit=5)

        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success

        if ok:
            klines = data.get("klines") or data.get("data") or data.get("items") or []
            if len(klines) == 0:
                ok = False
            else:
                first = klines[0]
                if not isinstance(first, dict):
                    ok = False
                else:
                    has_adj = "adj_factor" in first
                    ok = not has_adj

        if ok:
            klines = data.get("klines") or data.get("data") or data.get("items") or []
            results.append(tester._make_result(
                name, "kline_adj_factor",
                TestStatus.PASSED,
                f"OK, adj_factor 已移除, {len(klines)} 条",
                resp.response_time_ms,
            ))
        else:
            reason = "请求失败" if not resp.success else "无数据"
            if resp.success:
                klines = data.get("klines") or data.get("data") or data.get("items") or []
                if len(klines) > 0 and isinstance(klines[0], dict) and "adj_factor" in klines[0]:
                    reason = "adj_factor 字段仍然存在"
            results.append(tester._make_result(
                name, "kline_adj_factor",
                TestStatus.FAILED,
                reason,
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    # 额外验证: 必填字段仍然存在
    name = "adj_factor移除: CN - 必填字段完整性检查"
    resp = tester.client.v2_get_cnstock_klines(symbol="000001.SZ", limit=5)
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success
    if ok:
        klines = data.get("klines") or data.get("data") or data.get("items") or []
        if len(klines) > 0 and isinstance(klines[0], dict):
            first = klines[0]
            required = {"time", "symbol", "open", "high", "low", "close", "volume"}
            ok = required.issubset(first.keys())
            if ok:
                ok = (isinstance(first.get("open"), (int, float)) and
                      isinstance(first.get("close"), (int, float)) and
                      first.get("open") > 0 and first.get("close") > 0)

    results.append(tester._make_result(
        name, "kline_adj_factor",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        "必填字段完整" if ok else "必填字段缺失或类型异常",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    return results
