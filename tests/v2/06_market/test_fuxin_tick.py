"""
Fuxin 逐笔成交接口自测
覆盖: 三市场(CN/HK/US) x 正常数据/direction取值/增量拉取/count参数/代码格式/空数据
"""
from framework import BaseTester, TestStatus


def _get_body(resp) -> dict:
    """从响应中提取有效 body"""
    if not resp.success or not resp.data:
        return {}
    data = resp.data if isinstance(resp.data, dict) else {}
    if "body" in data:
        return data["body"] if isinstance(data["body"], dict) else {}
    return data


def test_fuxin_tick(tester: BaseTester) -> list:
    """逐笔成交接口完整测试"""
    results = []

    test_cases = [
        ("CN", "cnstock", "600519", "茅台 (sh)"),
        ("CN", "cnstock", "000001", "平安银行 (sz)"),
        ("HK", "hkstock", "00700", "腾讯"),
        ("US", "usstock", "AAPL", "苹果"),
    ]

    last_time_map = {}  # 保存 lastTime 用于增量测试

    # 1. 三市场基本查询
    for label, market, code, display in test_cases:
        name = f"逐笔成交: {label} - {display} ({code})"
        resp = tester.client.v2_fuxin_tick(market, code)
        body = _get_body(resp)

        ok = resp.success and body.get("success") is True
        if ok:
            ok = isinstance(body.get("symbol"), str) and body["symbol"] != ""

        ticks = body.get("ticks", [])

        if ok and isinstance(ticks, list) and len(ticks) > 0:
            # 有数据时验证字段
            item = ticks[0]
            required_keys = {"time", "timeStr", "price", "vol", "turnover", "direction"}
            ok = required_keys.issubset(item.keys())
            if ok:
                ok = isinstance(item["price"], (int, float)) and item["price"] >= 0
                ok = ok and isinstance(item["direction"], int) and item["direction"] in (0, 1, 2)
                ok = ok and isinstance(item["vol"], (int, float)) and item["vol"] >= 0

            # 检查所有 tick 的 direction 取值
            if ok:
                valid_dirs = all(
                    isinstance(t.get("direction"), int) and t["direction"] in (0, 1, 2)
                    for t in ticks
                )
                ok = ok and valid_dirs

            # 保存 lastTime
            lt = body.get("lastTime", "")
            if lt:
                last_time_map[code] = lt

            results.append(tester._make_result(
                name, "fuxin_tick", TestStatus.PASSED if ok else TestStatus.FAILED,
                f"OK, {len(ticks)} 条" if ok else "字段校验失败",
                resp.response_time_ms, resp.error if not ok else None,
            ))
        elif ok:
            # success=true 但空数据
            msg = body.get("message", "")
            results.append(tester._make_result(
                name, "fuxin_tick", TestStatus.SKIPPED,
                f"空数据（非交易时段）: {msg}",
                resp.response_time_ms,
            ))
        else:
            results.append(tester._make_result(
                name, "fuxin_tick", TestStatus.FAILED,
                f"请求失败: HTTP {resp.status_code}",
                resp.response_time_ms, resp.error,
            ))

    # 2. lastTime 增量拉取
    if last_time_map.get("600519"):
        name = "逐笔成交: CN - lastTime 增量拉取"
        resp = tester.client.v2_fuxin_tick("cnstock", "600519", last_time=last_time_map["600519"])
        body = _get_body(resp)
        ok = resp.success and body.get("success") is True
        if ok:
            ok = isinstance(body.get("ticks"), list)
            ok = ok and isinstance(body.get("lastTime"), str)
        results.append(tester._make_result(
            name, "fuxin_tick",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"OK, {len(body.get('ticks', []))} 条" if ok else "增量拉取失败",
            resp.response_time_ms, resp.error if not ok else None,
        ))
    else:
        results.append(tester._make_result(
            "逐笔成交: CN - lastTime 增量拉取", "fuxin_tick",
            TestStatus.SKIPPED, "跳过（无初始数据获取 lastTime）", 0,
        ))

    # 3. count 参数
    name = "逐笔成交: CN - count=5"
    resp = tester.client.v2_fuxin_tick("cnstock", "600519", count=5)
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True
    if ok:
        ticks = body.get("ticks", [])
        ok = isinstance(ticks, list)
        if ok and len(ticks) > 5:
            ok = False  # count=5 不应返回超过 5 条
    results.append(tester._make_result(
        name, "fuxin_tick",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"OK, {len(body.get('ticks', []))} 条" if ok else "count 参数失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    # 4. CN 带前缀 (sh600519)
    name = "逐笔成交: CN - 带前缀 sh600519"
    resp = tester.client.v2_fuxin_tick("cnstock", "sh600519")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True and body.get("symbol") == "600519"
    results.append(tester._make_result(
        name, "fuxin_tick",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbol={body.get('symbol')}" if ok else "前缀处理失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    # 5. CN 带后缀 (600519.SH)
    name = "逐笔成交: CN - 带后缀 600519.SH"
    resp = tester.client.v2_fuxin_tick("cnstock", "600519.SH")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True and body.get("symbol") == "600519"
    results.append(tester._make_result(
        name, "fuxin_tick",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbol={body.get('symbol')}" if ok else "后缀处理失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    return results
