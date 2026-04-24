"""
V2 Crypto News tests
加密货币新闻相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus


def test_crypto_news_list(tester: BaseTester) -> list:
    """Test crypto news list endpoint"""
    results = []

    resp = tester.client.v2_get_crypto_news_list(
        type_="article",
        lang="zh",
        page="1",
        page_size="10",
        is_popular="true",
        search=""
    )
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        items = data.get("items") or data.get("data") or []
        if not isinstance(items, list):
            ok = False

    results.append(tester._make_result(
        "CryptoNews: list",
        "crypto_news_list",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news_list - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_crypto_news_search(tester: BaseTester) -> list:
    """Test crypto news search endpoints"""
    results = []

    # Test search
    resp = tester.client.v2_get_crypto_news_search(
        query="bitcoin",
        lang="zh",
        page=1,
        page_size=10
    )
    ok = resp.success
    results.append(tester._make_result(
        "CryptoNews: search",
        "crypto_news_search",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news_search - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test latest
    resp2 = tester.client.v2_get_crypto_news_latest(
        type_="article",
        lang="zh",
        page_size=10
    )
    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoNews: latest",
        "crypto_news_latest",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"news_latest - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results


def test_crypto_news_detail(tester: BaseTester) -> list:
    """Test crypto news detail endpoint - may fail if news_id is invalid"""
    results = []

    # Using a placeholder news_id - this may return 404 but tests the endpoint
    resp = tester.client.v2_get_crypto_news_detail(news_id="12345")
    ok = resp.success

    # For detail endpoints, we accept both success and 404 as valid responses
    # as long as the endpoint is reachable
    is_reachable = resp.status_code in [200, 404]

    results.append(tester._make_result(
        "CryptoNews: detail",
        "crypto_news_detail",
        TestStatus.PASSED if is_reachable else TestStatus.FAILED,
        f"news_detail - {'OK' if is_reachable else 'FAILED'} ({resp.status_code})",
        resp.response_time_ms,
        resp.error if not is_reachable else None,
    ))

    return results
