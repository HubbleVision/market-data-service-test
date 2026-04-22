"""
AV 扩展 — 搜索与市场状态
覆盖: SYMBOL_SEARCH(无V2路由→SKIP), MARKET_STATUS, TOP_GAINERS_LOSERS
"""
from framework import BaseTester, TestStatus


def test_av_symbol_search(tester: BaseTester) -> list:
    """V2 无 symbol search 路由"""
    return [tester._make_result(
        "SYMBOL_SEARCH",
        "av_search",
        TestStatus.SKIPPED,
        "V2 无 /api/v2/usstock/search 等价路由",
        0,
    )]


def test_av_market_status(tester: BaseTester) -> list:
    """测试美股市场状态"""
    results = []

    resp = tester.client.v2_av_market_status()
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        markets = data.get("data") or []
        ok = isinstance(markets, list) and len(markets) > 0

    if ok:
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
    """测试涨跌排行"""
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
