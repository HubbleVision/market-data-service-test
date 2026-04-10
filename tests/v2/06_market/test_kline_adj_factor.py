"""
K线数据 adj_factor 字段移除验证
覆盖: 三市场 (CN/HK/US) K线数据确认不再包含 adj_factor 字段
"""
from framework import BaseTester, TestStatus


def _get_body(resp) -> dict:
    """从响应中提取 body（兼容有/无 body 包装层）"""
    if not resp.success or not resp.data:
        return {}
    data = resp.data if isinstance(resp.data, dict) else {}
    if "body" in data:
        return data["body"] if isinstance(data["body"], dict) else {}
    return data


def test_kline_adj_factor(tester: BaseTester) -> list:
    """验证 K线数据不再包含 adj_factor 字段"""
    results = []

    cases = [
        ("CN", "000001.SZ", "daily", "A股 日K"),
        ("CN", "600519.SH", "daily", "A股 日K (SH)"),
        ("CN", "830799.BJ", "daily", "A股 日K (BJ 北交所)"),
        ("HK", "00700.HK", "daily", "港股 日K"),
        ("US", "AAPL", "daily", "美股 日K"),
    ]

    for label, symbol, interval, display in cases:
        name = f"adj_factor移除: {label} - {display} ({symbol})"
        resp = tester.client.v1_get_stock_klines(symbol=symbol, interval=interval, limit=5)
        body = _get_body(resp)

        ok = resp.success
        if ok:
            ok = body.get("success") is True or isinstance(body.get("data"), list)
        if ok:
            klines = body.get("data", [])
            if len(klines) == 0:
                ok = False
            else:
                # 检查第一条 K 线不包含 adj_factor 字段
                first = klines[0]
                if not isinstance(first, dict):
                    ok = False
                else:
                    has_adj = "adj_factor" in first
                    ok = not has_adj

        if ok:
            klines = body.get("data", [])
            results.append(tester._make_result(
                name, "kline_adj_factor",
                TestStatus.PASSED,
                f"OK, adj_factor 已移除, {len(klines)} 条",
                resp.response_time_ms,
            ))
        else:
            reason = "请求失败" if not resp.success else "无数据"
            if resp.success:
                klines = body.get("data", [])
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
    resp = tester.client.v1_get_stock_klines(symbol="000001.SZ", interval="daily", limit=5)
    body = _get_body(resp)
    ok = resp.success
    if ok:
        klines = body.get("data", [])
        if len(klines) > 0 and isinstance(klines[0], dict):
            first = klines[0]
            required = {"time", "symbol", "open", "high", "low", "close", "volume"}
            ok = required.issubset(first.keys())
            if ok:
                # open/high/low/close 应为正数
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
