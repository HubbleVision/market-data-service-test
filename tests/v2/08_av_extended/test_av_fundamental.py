"""
AV 扩展 — 基本面数据
覆盖: INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW, EARNINGS_ESTIMATES,
      DIVIDENDS, SPLITS, SHARES_OUTSTANDING, ETF_PROFILE, LISTING_STATUS
"""
from framework import BaseTester, TestStatus

TEST_SYMBOLS = ["AAPL", "MSFT"]
TEST_ETF = ["SPY", "QQQ"]


def test_av_income_statement(tester: BaseTester) -> list:
    """利润表 INCOME_STATEMENT"""
    results = []
    for symbol in TEST_SYMBOLS:
        resp = tester.client.v2_av_income_statement(symbol=symbol)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or data.get("annualReports") or data.get("quarterlyReports") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            # 利润表关键字段
            ok = any(k in item for k in ["revenue", "totalRevenue", "grossProfit"])

        results.append(tester._make_result(
            f"INCOME_STATEMENT ({symbol})",
            "av_fundamental",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"利润表 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))
    return results


def test_av_balance_sheet(tester: BaseTester) -> list:
    """资产负债表 BALANCE_SHEET"""
    results = []
    for symbol in TEST_SYMBOLS:
        resp = tester.client.v2_av_balance_sheet(symbol=symbol)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = any(k in item for k in ["totalAssets", "totalLiabilities", "totalEquity"])

        results.append(tester._make_result(
            f"BALANCE_SHEET ({symbol})",
            "av_fundamental",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"资产负债表 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))
    return results


def test_av_cash_flow(tester: BaseTester) -> list:
    """现金流量表 CASH_FLOW"""
    results = []
    for symbol in TEST_SYMBOLS:
        resp = tester.client.v2_av_cash_flow(symbol=symbol)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = any(k in item for k in ["operatingCashflow", "capitalExpenditures", "freeCashFlow"])

        results.append(tester._make_result(
            f"CASH_FLOW ({symbol})",
            "av_fundamental",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"现金流量表 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))
    return results


def test_av_earnings_estimates(tester: BaseTester) -> list:
    """每股收益预估 EARNINGS_ESTIMATES"""
    results = []
    resp = tester.client.v2_av_earnings_estimates(symbol="AAPL")
    data = resp.data if isinstance(resp.data, dict) or resp.data else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list) and len(items) > 0

    if ok:
        item = items[0]
        ok = any(k in item for k in ["epsAvg", "earningsAvg", "numberOfAnalysts"])

    results.append(tester._make_result(
        "EARNINGS_ESTIMATES (AAPL)",
        "av_fundamental",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"盈利预估 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_dividends(tester: BaseTester) -> list:
    """历史股息 DIVIDENDS"""
    results = []
    resp = tester.client.v2_av_dividends(symbol="AAPL")
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list)

    results.append(tester._make_result(
        "DIVIDENDS (AAPL)",
        "av_fundamental",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"股息数据 - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_splits(tester: BaseTester) -> list:
    """历史拆股 SPLITS"""
    results = []
    resp = tester.client.v2_av_splits(symbol="AAPL")
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list)

    results.append(tester._make_result(
        "SPLITS (AAPL)",
        "av_fundamental",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"拆股数据 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_shares_outstanding(tester: BaseTester) -> list:
    """流通股数量 SHARES_OUTSTANDING"""
    results = []
    resp = tester.client.v2_av_shares_outstanding(symbol="AAPL")
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    results.append(tester._make_result(
        "SHARES_OUTSTANDING (AAPL)",
        "av_fundamental",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"流通股 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_etf_profile(tester: BaseTester) -> list:
    """ETF 档案 ETF_PROFILE"""
    results = []
    for symbol in TEST_ETF:
        resp = tester.client.v2_av_etf_profile(symbol=symbol)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            body = data.get("data") or data
            ok = isinstance(body, dict) and len(body) > 0

        results.append(tester._make_result(
            f"ETF_PROFILE ({symbol})",
            "av_fundamental",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"ETF档案 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))
    return results


def test_av_listing_status(tester: BaseTester) -> list:
    """上市/退市列表 LISTING_STATUS"""
    results = []
    resp = tester.client.v2_av_listing_status()
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        items = data.get("data") or []
        ok = isinstance(items, list) and len(items) > 0

    results.append(tester._make_result(
        "LISTING_STATUS",
        "av_fundamental",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"上市列表 - {'OK, ' + str(len(data.get('data', []))) + ' 条' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results
