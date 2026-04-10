"""
美股 Alpha Vantage 备用数据源接口测试
覆盖已接入 AV 降级的四个接口:
  1. GET /api/v2/usstock/securities  — 实时行情 (FUSO → AV → 503)
  2. GET /api/v2/usstock/min         — 分时数据 (FUSO → AV → 503)
  3. GET /api/v1/stock/usstock/daily — 日线数据 (FUSO → DB → AV → Tushare → 503)
  4. GET /api/v2/usstock/stocks      — V2日线   (StockKlineService 含 AV 降级)
"""
from framework import BaseTester, TestStatus

US_SYMBOLS = ["AAPL", "MSFT", "GOOGL"]


def _get_body(resp) -> dict:
    """从响应中提取有效 body（兼容有/无 body 包装层）"""
    if not resp.success or not resp.data:
        return {}
    data = resp.data if isinstance(resp.data, dict) else {}
    if "body" in data:
        return data["body"] if isinstance(data["body"], dict) else {}
    return data


def test_usstock_av_securities(tester: BaseTester) -> list:
    """测试 /v2/usstock/securities 实时行情接口（含 AV 降级）"""
    results = []

    # 1. 多 code 查询
    codes = "AAPL,MSFT"
    resp = tester.client.v2_get_usstock_securities(codes=codes)
    data = resp.data if isinstance(resp.data, dict) else {}

    ok = resp.success and data.get("success") is True
    if ok:
        quote_data = data.get("data")
        ok = isinstance(quote_data, dict) and len(quote_data) > 0
    if ok:
        for code in codes.split(","):
            if code.strip() not in quote_data:
                ok = False
                break

    results.append(tester._make_result(
        "AV备用: securities 多code查询",
        "usstock_av_securities",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"securities({codes}) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. 单 code 数据校验 — 通用字段（FUSO / AV 均返回）
    resp2 = tester.client.v2_get_usstock_securities(codes="AAPL")
    data2 = resp2.data if isinstance(resp2.data, dict) else {}
    ok2 = resp2.success and data2.get("success") is True

    source = None
    item = {}
    if ok2:
        quote = data2.get("data", {})
        item = quote.get("AAPL", {})
        ok2 = isinstance(item, dict) and len(item) > 0
    if ok2:
        # 通用字段校验（FUSO 用 vol，AV 用 volume，兼容两种）
        required = ["price", "open", "high", "low"]
        ok2 = all(f in item for f in required)
    if ok2:
        ok2 = "vol" in item or "volume" in item
    if ok2:
        ok2 = isinstance(item.get("price"), (int, float)) and item["price"] > 0
    if ok2:
        vol_val = item.get("volume") or item.get("vol")
        ok2 = isinstance(vol_val, (int, float))

    # 检测数据源
    if ok2 and item.get("source") == "alpha_vantage":
        source = "alpha_vantage"
        # AV 特有字段校验
        ok2 = isinstance(item.get("chgVal"), (int, float))
        ok2 = ok2 and isinstance(item.get("chgPct"), (int, float))
        ok2 = ok2 and isinstance(item.get("pClose"), (int, float))

    results.append(tester._make_result(
        f"AV备用: securities 单code数据校验 (source={source or 'fosun'})",
        "usstock_av_securities_data",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"securities(AAPL) fields check, source={source or 'fosun'}" if ok2 else "字段校验失败",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    # 3. 响应结构校验 — timestamp 存在
    ok3 = resp2.success
    data3 = resp2.data if isinstance(resp2.data, dict) else {}
    if ok3:
        ok3 = isinstance(data3.get("timestamp"), (int, float))
    if ok3:
        ok3 = isinstance(data3.get("message"), str)

    results.append(tester._make_result(
        "AV备用: securities 响应结构",
        "usstock_av_securities_structure",
        TestStatus.PASSED if ok3 else TestStatus.FAILED,
        f"structure check - {'OK' if ok3 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok3 else None,
    ))

    # 4. 无效 code 处理
    resp4 = tester.client.v2_get_usstock_securities(codes="INVALID_CODE_XXXXX")
    ok4 = resp4.success
    data4 = resp4.data if isinstance(resp4.data, dict) else {}
    if ok4:
        ok4 = data4.get("success") is True

    results.append(tester._make_result(
        "AV备用: securities 无效code",
        "usstock_av_securities_invalid",
        TestStatus.PASSED if ok4 else TestStatus.FAILED,
        f"invalid code handling - {'OK' if ok4 else 'FAILED'}",
        resp4.response_time_ms,
        resp4.error if not ok4 else None,
    ))

    return results


def test_usstock_av_min(tester: BaseTester) -> list:
    """测试 /v2/usstock/min 分时数据接口（含 AV 降级）"""
    results = []

    test_cases = [
        ("AAPL", "苹果"),
        ("MSFT", "微软"),
    ]

    for code, display in test_cases:
        name = f"AV备用: min {display} ({code})"
        resp = tester.client.v2_fuxin_min("usstock", code)
        body = _get_body(resp)

        ok = resp.success and body.get("success") is True
        if ok:
            ok = isinstance(body.get("symbol"), str) and body["symbol"] != ""
        if ok:
            ok = isinstance(body.get("timestamp"), (int, float))
        has_data = ok and isinstance(body.get("data"), list) and len(body["data"]) > 0

        if has_data:
            # 数据项字段校验
            item = body["data"][0]
            required_keys = {"time", "timeStr", "price", "avg", "volume", "turnover"}
            ok = required_keys.issubset(item.keys())
            if ok:
                ok = isinstance(item["price"], (int, float)) and item["price"] >= 0
                ok = ok and isinstance(item["volume"], (int, float))
                ok = ok and isinstance(item["timeStr"], str)
            if ok:
                ok = isinstance(body.get("pClose"), (int, float))

            results.append(tester._make_result(
                name, "usstock_av_min",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"OK, {len(body['data'])} 条" if ok else "字段校验失败",
                resp.response_time_ms, resp.error if not ok else None,
            ))
        elif ok:
            # success=true 但空数据（非交易时段）
            msg = body.get("message", "")
            results.append(tester._make_result(
                name, "usstock_av_min",
                TestStatus.SKIPPED,
                f"空数据（非交易时段）: {msg}",
                resp.response_time_ms,
            ))
        else:
            results.append(tester._make_result(
                name, "usstock_av_min",
                TestStatus.FAILED,
                f"请求失败: HTTP {resp.status_code}",
                resp.response_time_ms, resp.error,
            ))

    # ktype=min5 参数测试
    name = "AV备用: min AAPL ktype=min5"
    resp = tester.client.v2_fuxin_min("usstock", "AAPL", ktype="min5")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True
    has_data = ok and isinstance(body.get("data"), list) and len(body["data"]) > 0

    if has_data:
        results.append(tester._make_result(
            name, "usstock_av_min",
            TestStatus.PASSED, f"OK, {len(body['data'])} 条",
            resp.response_time_ms,
        ))
    elif ok:
        results.append(tester._make_result(
            name, "usstock_av_min",
            TestStatus.SKIPPED, "空数据（非交易时段）",
            resp.response_time_ms,
        ))
    else:
        results.append(tester._make_result(
            name, "usstock_av_min",
            TestStatus.FAILED, f"请求失败: HTTP {resp.status_code}",
            resp.response_time_ms, resp.error,
        ))

    return results


def test_usstock_av_v1_daily(tester: BaseTester) -> list:
    """测试 /api/v1/stock/usstock/daily V1日线接口（含 AV 降级）"""
    results = []

    for symbol in US_SYMBOLS:
        resp = tester.client.get_usstock_daily(symbol=symbol, limit=10)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}

        source = None
        if ok:
            source = data.get("source", "")
            items = data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0
        if ok:
            # OHLCV 字段校验
            item = items[0]
            required = ["time", "open", "high", "low", "close", "volume"]
            ok = all(f in item for f in required)
        if ok:
            ok = isinstance(data.get("total"), (int, float)) and data["total"] > 0

        label = f"source={source}" if source else "source未标注"
        results.append(tester._make_result(
            f"AV备用: V1 daily ({symbol}) [{label}]",
            "usstock_av_v1_daily",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"v1/daily({symbol}) {label} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    # 带 startDate/endDate 测试
    resp2 = tester.client.get_usstock_daily(
        symbol="AAPL", start_date="20250101", end_date="20250301", limit=10
    )
    ok2 = resp2.success
    data2 = resp2.data if isinstance(resp2.data, dict) else {}
    if ok2:
        items2 = data2.get("data") or []
        ok2 = isinstance(items2, list) and len(items2) > 0

    results.append(tester._make_result(
        "AV备用: V1 daily (带日期范围)",
        "usstock_av_v1_daily",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"v1/daily(AAPL, 20250101-20250301) - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results


def test_usstock_av_v2_daily(tester: BaseTester) -> list:
    """测试 /api/v2/usstock/stocks V2日线接口（StockKlineService 含 AV 降级）"""
    results = []

    for symbol in US_SYMBOLS:
        resp = tester.client.v2_get_usstock_daily(symbol=symbol, limit=10)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}

        source = None
        if ok:
            source = data.get("source", "")
            items = data.get("klines") or data.get("items") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            # 数据项基本结构校验
            item = items[0]
            required = ["time", "open", "high", "low", "close"]
            ok = all(f in item for f in required)

        label = f"source={source}" if source else "source未标注"
        results.append(tester._make_result(
            f"AV备用: V2 daily ({symbol}) [{label}]",
            "usstock_av_v2_daily",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"v2/usstock/stocks({symbol}) {label} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    # 带 startDate/endDate 测试
    resp2 = tester.client.v2_get_usstock_daily(
        symbol="AAPL", start_date="20250101", end_date="20250301", limit=10
    )
    ok2 = resp2.success
    data2 = resp2.data if isinstance(resp2.data, dict) else {}
    if ok2:
        items2 = data2.get("klines") or data2.get("items") or data2.get("data") or []
        ok2 = isinstance(items2, list) and len(items2) > 0

    results.append(tester._make_result(
        "AV备用: V2 daily (带日期范围)",
        "usstock_av_v2_daily",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"v2/usstock/stocks(AAPL, 20250101-20250301) - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results
