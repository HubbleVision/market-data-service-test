"""
Symbol 标准化与市场推断测试
覆盖:
  - 无后缀 A 股: 6位纯数字自动推断为 A 股，自动补全交易所后缀 (.SH/.SZ/.BJ)
  - 无后缀港股: 5位纯数字自动推断为港股，补全 .HK
  - 无后缀美股: 含字母代码默认美股，不补后缀
  - 北交所 .BJ 支持
  - US .US 后缀 trim (klines/indicators)
  - 已有后缀的原样返回
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


def test_symbol_normalize(tester: BaseTester) -> list:
    """Symbol 标准化与市场推断完整测试"""
    results = []

    # ===== 1. K线接口: 无后缀 6位纯数字 → A 股 =====
    cases_kline_cn = [
        ("600519", "600519.SH", "茅台 6位→SH"),
        ("000001", "000001.SZ", "平安银行 6位→SZ"),
        ("300750", "300750.SZ", "宁德时代 3开头→SZ"),
        ("688981", "688981.SH", "中芯国际 688→SH"),
        ("830799", "830799.BJ", "北交所 8开头→BJ"),
    ]
    for raw, expected_suffix, display in cases_kline_cn:
        name = f"Symbol标准化: K线 无后缀 {raw} → {expected_suffix}"
        resp = tester.client.v1_get_stock_klines(symbol=raw, limit=5)
        body = _get_body(resp)

        ok = resp.success
        if ok:
            ok = isinstance(body.get("symbol"), str) and body.get("symbol") == expected_suffix
        if ok:
            ok = body.get("market") == "cn"

        results.append(tester._make_result(
            name, "symbol_normalize",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"symbol={body.get('symbol')}, market={body.get('market')}" if ok else f"期望 symbol={expected_suffix}, 实际={body.get('symbol')}",
            resp.response_time_ms, resp.error if not ok else None,
        ))

    # ===== 2. K线接口: 无后缀 5位纯数字 → 港股 =====
    cases_kline_hk = [
        ("00700", "00700.HK", "腾讯 5位→HK"),
        ("00941", "00941.HK", "中国移动 5位→HK"),
    ]
    for raw, expected_suffix, display in cases_kline_hk:
        name = f"Symbol标准化: K线 无后缀 {raw} → {expected_suffix}"
        resp = tester.client.v1_get_stock_klines(symbol=raw, limit=5)
        body = _get_body(resp)

        ok = resp.success
        if ok:
            ok = isinstance(body.get("symbol"), str) and body.get("symbol") == expected_suffix
        if ok:
            ok = body.get("market") == "hk"

        results.append(tester._make_result(
            name, "symbol_normalize",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"symbol={body.get('symbol')}, market={body.get('market')}" if ok else f"期望 symbol={expected_suffix}, 实际={body.get('symbol')}",
            resp.response_time_ms, resp.error if not ok else None,
        ))

    # ===== 3. K线接口: 含字母 → 美股 =====
    cases_kline_us = [
        ("AAPL", "AAPL", "苹果 含字母→US"),
        ("TSLA", "TSLA", "特斯拉 含字母→US"),
    ]
    for raw, expected, display in cases_kline_us:
        name = f"Symbol标准化: K线 {raw} → US"
        resp = tester.client.v1_get_stock_klines(symbol=raw, limit=5)
        body = _get_body(resp)

        ok = resp.success
        if ok:
            ok = isinstance(body.get("symbol"), str) and body.get("symbol") == expected
        if ok:
            ok = body.get("market") == "us"

        results.append(tester._make_result(
            name, "symbol_normalize",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"symbol={body.get('symbol')}, market={body.get('market')}" if ok else f"期望 symbol={expected}, 实际={body.get('symbol')}",
            resp.response_time_ms, resp.error if not ok else None,
        ))

    # ===== 4. K线接口: US .US 后缀 trim =====
    name = "Symbol标准化: K线 AAPL.US → trim .US"
    resp = tester.client.v1_get_stock_klines(symbol="AAPL.US", limit=5)
    body = _get_body(resp)

    ok = resp.success
    if ok:
        # 服务端应 trim .US，返回 AAPL
        ok = isinstance(body.get("symbol"), str) and body.get("symbol") == "AAPL"
    if ok:
        ok = body.get("market") == "us"

    results.append(tester._make_result(
        name, "symbol_normalize",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbol={body.get('symbol')}, market={body.get('market')}" if ok else f"期望 symbol=AAPL, 实际={body.get('symbol')}",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    # ===== 5. K线接口: 已有后缀原样返回 =====
    cases_with_suffix = [
        ("000001.SZ", "cn", "已有 .SZ 后缀"),
        ("600519.SH", "cn", "已有 .SH 后缀"),
        ("00700.HK", "hk", "已有 .HK 后缀"),
        ("830799.BJ", "cn", "已有 .BJ 后缀(北交所)"),
    ]
    for raw, expected_market, display in cases_with_suffix:
        name = f"Symbol标准化: K线 {raw} → {expected_market}"
        resp = tester.client.v1_get_stock_klines(symbol=raw, limit=5)
        body = _get_body(resp)

        ok = resp.success
        if ok:
            ok = isinstance(body.get("symbol"), str) and body.get("symbol") == raw
        if ok:
            ok = body.get("market") == expected_market

        results.append(tester._make_result(
            name, "symbol_normalize",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"symbol={body.get('symbol')}, market={body.get('market')}" if ok else f"期望 symbol={raw}, 实际={body.get('symbol')}",
            resp.response_time_ms, resp.error if not ok else None,
        ))

    # ===== 6. 指标接口: 无后缀市场推断 =====
    cases_indicator = [
        ("600519", "600519.SH", "cn", "指标: 6位→SH"),
        ("00700", "00700.HK", "hk", "指标: 5位→HK"),
        ("AAPL", "AAPL", "us", "指标: 字母→US"),
    ]
    for raw, expected_sym, expected_mkt, display in cases_indicator:
        name = f"Symbol标准化: 指标 {raw} → {expected_sym}"
        resp = tester.client.v1_get_stock_indicators(symbol=raw, limit=5)
        body = _get_body(resp)

        ok = resp.success
        if ok:
            ok = isinstance(body.get("symbol"), str) and body.get("symbol") == expected_sym
        if ok:
            ok = body.get("market") == expected_mkt

        results.append(tester._make_result(
            name, "symbol_normalize",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"symbol={body.get('symbol')}, market={body.get('market')}" if ok else f"期望 symbol={expected_sym}, 实际={body.get('symbol')}",
            resp.response_time_ms, resp.error if not ok else None,
        ))

    return results
