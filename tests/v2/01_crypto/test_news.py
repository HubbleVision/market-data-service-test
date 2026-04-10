"""
V2 Crypto News test
Tests for news list, detail, search, and latest endpoints
"""
from framework import BaseTester, TestResult, TestStatus


def test_news(tester: BaseTester) -> list:
    """Test V2 crypto news endpoints (list, detail, search, latest)"""
    results = []

    # ---- 1. News List: flash news (type=1), zh ----
    resp = tester.client.v2_get_crypto_news_list(
        type_="1", lang="zh", page="1", page_size="10",
        is_popular="false", search=""
    )
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data", {}).get("list") is not None
    results.append(tester._make_result(
        "News: list flash zh",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/list type=1 lang=zh - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 2. News List: articles (type=2), zh ----
    resp = tester.client.v2_get_crypto_news_list(
        type_="2", lang="zh", page="1", page_size="10",
        is_popular="false", search=""
    )
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data", {}).get("list") is not None
    results.append(tester._make_result(
        "News: list articles zh",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/list type=2 lang=zh - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 3. News List: flash news, en ----
    resp = tester.client.v2_get_crypto_news_list(
        type_="1", lang="en", page="1", page_size="5",
        is_popular="false", search=""
    )
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data", {}).get("list") is not None
    results.append(tester._make_result(
        "News: list flash en",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/list type=1 lang=en - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 4. News List: search with keyword ----
    resp = tester.client.v2_get_crypto_news_list(
        type_="1", lang="zh", page="1", page_size="10",
        is_popular="false", search="BTC"
    )
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data", {}).get("list") is not None
    results.append(tester._make_result(
        "News: list search BTC",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/list search=BTC - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 5. News List: popular ----
    resp = tester.client.v2_get_crypto_news_list(
        type_="1", lang="zh", page="1", page_size="10",
        is_popular="true", search=""
    )
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data", {}).get("list") is not None
    results.append(tester._make_result(
        "News: list popular",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/list isPopular=true - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 6. News List: structured response validation ----
    resp = tester.client.v2_get_crypto_news_list(
        type_="1", lang="zh", page="1", page_size="5",
        is_popular="false", search=""
    )
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    msg = ""
    if ok:
        ok = bool(data.get("success"))
        if ok:
            list_data = data.get("data", {})
            has_list = list_data.get("list") is not None
            has_pagination = list_data.get("pagination") is not None
            if not has_list:
                ok = False
                msg = "missing list field"
            elif not has_pagination:
                ok = False
                msg = "missing pagination field"
            elif list_data.get("list"):
                item = list_data["list"][0]
                required = ["id", "title", "ts"]
                missing = [f for f in required if f not in item]
                if missing:
                    ok = False
                    msg = f"item missing {', '.join(missing)}"
    results.append(tester._make_result(
        "News: list structure validation",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/list structure - {'OK' if ok else msg}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 7. News Detail ----
    resp = tester.client.v2_get_crypto_news_detail(news_id="1")
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data") is not None
    results.append(tester._make_result(
        "News: detail",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/detail - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 8. News Search (DB full-text search) ----
    resp = tester.client.v2_get_crypto_news_search(query="Bitcoin", lang="zh", page=1, page_size=5)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data") is not None
    results.append(tester._make_result(
        "News: search",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/search q=Bitcoin - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 9. News Search: structure validation ----
    resp = tester.client.v2_get_crypto_news_search(query="BTC", page=1, page_size=5)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    msg = ""
    if ok:
        ok = bool(data.get("success"))
        if ok:
            search_data = data.get("data", {})
            has_items = search_data.get("items") is not None
            has_total = search_data.get("total") is not None
            if not has_items or not has_total:
                ok = False
                msg = f"missing fields: items={has_items}, total={has_total}"
    results.append(tester._make_result(
        "News: search structure",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/search structure - {'OK' if ok else msg}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 10. News Latest ----
    resp = tester.client.v2_get_crypto_news_latest(type_="1", lang="zh", page_size=5)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data") is not None
    results.append(tester._make_result(
        "News: latest flash zh",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/latest type=1 lang=zh - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 11. News Latest: articles en ----
    resp = tester.client.v2_get_crypto_news_latest(type_="2", lang="en", page_size=5)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success")) and data.get("data") is not None
    results.append(tester._make_result(
        "News: latest articles en",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/latest type=2 lang=en - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # ---- 12. News Latest: no type (all types) ----
    resp = tester.client.v2_get_crypto_news_latest(lang="zh", page_size=10)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = bool(data.get("success"))
    results.append(tester._make_result(
        "News: latest all types",
        "crypto_news",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"news/latest no type filter - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
