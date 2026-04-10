"""
Fuxin 分时数据接口自测
覆盖: 三市场(CN/HK/US) x 正常数据/代码格式/响应结构/空数据
"""
from framework import BaseTester, TestStatus


# 市场前缀映射
MARKET_PREFIX = {"cn": "cnstock", "hk": "hkstock", "us": "usstock"}


def _get_body(resp) -> dict:
    """从响应中提取有效 body（兼容有/无 body 包装层）"""
    if not resp.success or not resp.data:
        return {}
    data = resp.data if isinstance(resp.data, dict) else {}
    # brokerq/orderbook/tick 用 body 包装层
    if "body" in data:
        return data["body"] if isinstance(data["body"], dict) else {}
    return data


def test_fuxin_min(tester: BaseTester) -> list:
    """分时数据接口完整测试"""
    results = []

    test_cases = [
        ("CN", "cnstock", "600519", "茅台 (sh)"),
        ("CN", "cnstock", "000001", "平安银行 (sz)"),
        ("HK", "hkstock", "00700", "腾讯"),
        ("US", "usstock", "AAPL", "苹果"),
    ]

    # 1. 三市场基本查询
    for label, market, code, display in test_cases:
        name = f"分时数据: {label} - {display} ({code})"
        resp = tester.client.v2_fuxin_min(market, code)
        body = _get_body(resp)

        ok = resp.success and body.get("success") is True
        if ok:
            ok = isinstance(body.get("symbol"), str) and body["symbol"] != ""
        if ok:
            ok = isinstance(body.get("timestamp"), (int, float))
        has_data = ok and isinstance(body.get("data"), list) and len(body["data"]) > 0

        if has_data:
            # 有数据时验证字段类型
            item = body["data"][0]
            required_keys = {"time", "timeStr", "price", "avg", "volume", "turnover"}
            ok = required_keys.issubset(item.keys())
            if ok:
                ok = isinstance(item["price"], (int, float)) and item["price"] >= 0
                ok = ok and isinstance(item["volume"], (int, float))
                ok = ok and isinstance(item["timeStr"], str)

            results.append(tester._make_result(
                name, "fuxin_min", TestStatus.PASSED if ok else TestStatus.FAILED,
                f"OK, {len(body['data'])} 条" if ok else "字段校验失败",
                resp.response_time_ms, resp.error if not ok else None,
            ))
        elif ok:
            # success=true 但空数据（非交易时段）
            msg = body.get("message", "")
            results.append(tester._make_result(
                name, "fuxin_min", TestStatus.SKIPPED,
                f"空数据（非交易时段）: {msg}",
                resp.response_time_ms,
            ))
        else:
            results.append(tester._make_result(
                name, "fuxin_min", TestStatus.FAILED,
                f"请求失败: HTTP {resp.status_code}",
                resp.response_time_ms, resp.error,
            ))

    # 2. CN 带前缀格式 (sh600519)
    name = "分时数据: CN - 带前缀 sh600519"
    resp = tester.client.v2_fuxin_min("cnstock", "sh600519")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True and body.get("symbol") == "600519"
    results.append(tester._make_result(
        name, "fuxin_min",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbol={body.get('symbol')}" if ok else "前缀处理失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    # 3. CN 带后缀格式 (600519.SH)
    name = "分时数据: CN - 带后缀 600519.SH"
    resp = tester.client.v2_fuxin_min("cnstock", "600519.SH")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True and body.get("symbol") == "600519"
    results.append(tester._make_result(
        name, "fuxin_min",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbol={body.get('symbol')}" if ok else "后缀处理失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    # 4. ktype 参数
    name = "分时数据: CN - ktype=min5"
    resp = tester.client.v2_fuxin_min("cnstock", "600519", ktype="min5")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True
    results.append(tester._make_result(
        name, "fuxin_min",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        "OK" if ok else "ktype 参数失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    return results
