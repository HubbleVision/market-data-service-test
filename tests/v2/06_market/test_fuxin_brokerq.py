"""
Fuxin 五档买卖盘接口自测
覆盖: 三市场(CN/HK/US) x 正常数据/档位排序/代码格式/空数据
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


def test_fuxin_brokerq(tester: BaseTester) -> list:
    """五档买卖盘接口完整测试"""
    results = []

    test_cases = [
        ("CN", "cnstock", "600519", "茅台 (sh)"),
        ("CN", "cnstock", "000001", "平安银行 (sz)"),
        ("HK", "hkstock", "00700", "腾讯"),
        ("US", "usstock", "AAPL", "苹果"),
    ]

    # 1. 三市场基本查询
    for label, market, code, display in test_cases:
        name = f"五档买卖盘: {label} - {display} ({code})"
        resp = tester.client.v2_fuxin_brokerq(market, code)
        body = _get_body(resp)

        ok = resp.success and body.get("success") is True
        if ok:
            ok = isinstance(body.get("symbol"), str) and body["symbol"] != ""

        bid = body.get("bid", [])
        ask = body.get("ask", [])

        if ok and isinstance(bid, list) and isinstance(ask, list) and (len(bid) > 0 or len(ask) > 0):
            # 有数据时验证字段和排序
            if len(bid) > 0:
                item = bid[0]
                ok = ok and "price" in item and "vol" in item
                ok = ok and isinstance(item["price"], (int, float)) and item["price"] > 0
                # bid 应降序
                prices = [b["price"] for b in bid if isinstance(b.get("price"), (int, float))]
                ok = ok and prices == sorted(prices, reverse=True)

            if len(ask) > 0:
                item = ask[0]
                ok = ok and "price" in item and "vol" in item
                ok = ok and isinstance(item["price"], (int, float)) and item["price"] > 0
                # ask 应升序
                prices = [a["price"] for a in ask if isinstance(a.get("price"), (int, float))]
                ok = ok and prices == sorted(prices)

            results.append(tester._make_result(
                name, "fuxin_brokerq", TestStatus.PASSED if ok else TestStatus.FAILED,
                f"OK, bid={len(bid)}, ask={len(ask)}" if ok else "数据校验失败",
                resp.response_time_ms, resp.error if not ok else None,
            ))
        elif ok:
            # success=true 但空数据
            msg = body.get("message", "")
            results.append(tester._make_result(
                name, "fuxin_brokerq", TestStatus.SKIPPED,
                f"空数据（非交易时段/停牌）: {msg}",
                resp.response_time_ms,
            ))
        else:
            results.append(tester._make_result(
                name, "fuxin_brokerq", TestStatus.FAILED,
                f"请求失败: HTTP {resp.status_code}",
                resp.response_time_ms, resp.error,
            ))

    # 2. CN 带前缀 (sz000001)
    name = "五档买卖盘: CN - 带前缀 sz000001"
    resp = tester.client.v2_fuxin_brokerq("cnstock", "sz000001")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True and body.get("symbol") == "000001"
    results.append(tester._make_result(
        name, "fuxin_brokerq",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbol={body.get('symbol')}" if ok else "前缀处理失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    # 3. CN 带后缀 (000001.SZ)
    name = "五档买卖盘: CN - 带后缀 000001.SZ"
    resp = tester.client.v2_fuxin_brokerq("cnstock", "000001.SZ")
    body = _get_body(resp)
    ok = resp.success and body.get("success") is True and body.get("symbol") == "000001"
    results.append(tester._make_result(
        name, "fuxin_brokerq",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"symbol={body.get('symbol')}" if ok else "后缀处理失败",
        resp.response_time_ms, resp.error if not ok else None,
    ))

    return results
