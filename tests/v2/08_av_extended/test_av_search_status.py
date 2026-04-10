"""
AV 扩展 — 搜索与市场状态
覆盖: SYMBOL_SEARCH, MARKET_STATUS, TOP_GAINERS_LOSERS
"""
from framework import BaseTester, TestStatus


def test_av_symbol_search(tester: BaseTester) -> list:
    """测试股票搜索 SYMBOL_SEARCH"""
    results = []
    test_keywords = ["AAPL", "Tesla", "SPY"]

    for kw in test_keywords:
        resp = tester.client.v2_av_symbol_search(keywords=kw)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or data.get("results") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            # 校验搜索结果包含关键字段
            item = items[0] if isinstance(items, list) else items
            ok = isinstance(item.get("symbol"), str) and len(item["symbol"]) > 0

        results.append(tester._make_result(
            f"SYMBOL_SEARCH ({kw})",
            "av_search",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"搜索 '{kw}' - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    # 边界: 空关键词
    resp_empty = tester.client.v2_av_symbol_search(keywords="")
    ok_empty = resp_empty.success
    results.append(tester._make_result(
        "SYMBOL_SEARCH (空关键词)",
        "av_search",
        TestStatus.PASSED if ok_empty else TestStatus.FAILED,
        "空关键词处理",
        resp_empty.response_time_ms,
        resp_empty.error if not ok_empty else None,
    ))

    return results


def test_av_market_status(tester: BaseTester) -> list:
    """测试全球市场状态 MARKET_STATUS"""
    results = []

    resp = tester.client.v2_av_market_status()
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        markets = data.get("data") or []
        ok = isinstance(markets, list) and len(markets) > 0

    if ok:
        # 校验市场条目字段
        item = markets[0]
        ok = isinstance(item.get("exchange"), str)
        if ok:
            ok = "status" in item or "is_open" in item

    results.append(tester._make_result(
        "MARKET_STATUS",
        "av_market_status",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"{'OK, ' + str(len(data.get('data', []))) + ' 个市场' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_av_top_gainers_losers(tester: BaseTester) -> list:
    """测试涨跌排行 TOP_GAINERS_LOSERS"""
    results = []

    directions = ["top_gainers", "top_losers", "most_actively_traded"]
    for direction in directions:
        resp = tester.client.v2_av_top_gainers_losers(direction=direction)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = isinstance(item.get("ticker"), str) and len(item["ticker"]) > 0

        results.append(tester._make_result(
            f"TOP_GAINERS_LOSERS ({direction})",
            "av_top_gainers_losers",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
