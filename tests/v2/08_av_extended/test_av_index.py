"""
AV 扩展 — 指数数据 (P1)
覆盖: INDEX_DATA, INDEX_CATALOG
"""
from framework import BaseTester, TestStatus

TEST_INDICES = ["SPX", "DJI", "COMP", "NDX", "VIX"]


def test_av_index_data(tester: BaseTester) -> list:
    """指数数据 INDEX_DATA"""
    results = []

    for symbol in TEST_INDICES:
        resp = tester.client.v2_av_index_data(symbol=symbol, limit=10)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or data.get("klines") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = all(f in item for f in ["time", "close"])

        results.append(tester._make_result(
            f"INDEX_DATA ({symbol})",
            "av_index",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"指数 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_index_catalog(tester: BaseTester) -> list:
    """指数目录 INDEX_CATALOG"""
    results = []
    resp = tester.client.v2_av_index_catalog()
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list) and len(items) > 0

    results.append(tester._make_result(
        "INDEX_CATALOG",
        "av_index",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"指数目录 - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results
