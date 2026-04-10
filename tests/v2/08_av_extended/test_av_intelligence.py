"""
AV 扩展 — Alpha Intelligence (P1)
覆盖: NEWS_SENTIMENT, INSIDER_TRANSACTIONS, INSTITUTIONAL_HOLDINGS,
      ANALYTICS_FIXED_WINDOW, ANALYTICS_SLIDING_WINDOW
"""
from framework import BaseTester, TestStatus


def test_av_news_sentiment(tester: BaseTester) -> list:
    """新闻情绪 NEWS_SENTIMENT"""
    results = []

    # 按 ticker 查询
    resp = tester.client.v2_av_news_sentiment(tickers="AAPL", limit=10)
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or data.get("feed") or []
        ok = isinstance(items, list) and len(items) > 0

    if ok:
        item = items[0]
        ok = isinstance(item.get("title"), str) and len(item["title"]) > 0

    results.append(tester._make_result(
        "NEWS_SENTIMENT (AAPL)",
        "av_intelligence",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"新闻情绪 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 按 topic 查询
    resp2 = tester.client.v2_av_news_sentiment(topics="technology", limit=5)
    data2 = resp2.data if isinstance(resp2.data, dict) else {}
    ok2 = resp2.success and data2.get("success") is True

    results.append(tester._make_result(
        "NEWS_SENTIMENT (topic=technology)",
        "av_intelligence",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"新闻情绪(topic) - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results


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
    """高级分析 (固定窗口)"""
    results = []
    resp = tester.client.v2_av_analytics_fixed_window(
        symbol="AAPL",
        calculations="ROR",
        start_date="2024-01-01",
        end_date="2024-12-31",
    )
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    results.append(tester._make_result(
        "ANALYTICS_FIXED_WINDOW (AAPL ROR)",
        "av_intelligence",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"固定窗口分析 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_analytics_sliding_window(tester: BaseTester) -> list:
    """高级分析 (滑动窗口)"""
    results = []
    resp = tester.client.v2_av_analytics_sliding_window(
        symbol="AAPL",
        calculations="MEAN,STDDEV",
        window=20,
    )
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    results.append(tester._make_result(
        "ANALYTICS_SLIDING_WINDOW (AAPL MEAN,STDDEV)",
        "av_intelligence",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"滑动窗口分析 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results
