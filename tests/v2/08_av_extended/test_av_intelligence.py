"""
AV 扩展 — Alpha Intelligence (V2)
覆盖: INSIDER_TRANSACTIONS, INSTITUTIONAL_HOLDINGS
SKIP: NEWS_SENTIMENT(无路由), ANALYTICS_FIXED_WINDOW(无路由), ANALYTICS_SLIDING_WINDOW(无路由)
"""
from framework import BaseTester, TestStatus


def test_av_news_sentiment(tester: BaseTester) -> list:
    """V2 无 news sentiment 路由"""
    return [tester._make_result(
        "NEWS_SENTIMENT",
        "av_intelligence",
        TestStatus.SKIPPED,
        "V2 无 /api/v2/usstock/news 路由",
        0,
    )]


def test_av_insider_transactions(tester: BaseTester) -> list:
    """内部交易 INSIDER_TRANSACTIONS"""
    results = []
    resp = tester.client.v2_av_insider_transactions(symbol="AAPL")
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list)

    results.append(tester._make_result(
        "INSIDER_TRANSACTIONS (AAPL)",
        "av_intelligence",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"内部交易 - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_institutional_holdings(tester: BaseTester) -> list:
    """机构持仓 INSTITUTIONAL_HOLDINGS"""
    results = []
    resp = tester.client.v2_av_institutional_holdings(symbol="AAPL")
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list)

    results.append(tester._make_result(
        "INSTITUTIONAL_HOLDINGS (AAPL)",
        "av_intelligence",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"机构持仓 - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_analytics_fixed_window(tester: BaseTester) -> list:
    """V2 无 analytics 路由"""
    return [tester._make_result(
        "ANALYTICS_FIXED_WINDOW",
        "av_intelligence",
        TestStatus.SKIPPED,
        "V2 无 analytics 路由",
        0,
    )]


def test_av_analytics_sliding_window(tester: BaseTester) -> list:
    """V2 无 analytics 路由"""
    return [tester._make_result(
        "ANALYTICS_SLIDING_WINDOW",
        "av_intelligence",
        TestStatus.SKIPPED,
        "V2 无 analytics 路由",
        0,
    )]
