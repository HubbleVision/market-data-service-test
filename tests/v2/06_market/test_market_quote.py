"""
V2 Market Quote tests: unified real-time quote across HK/CN/US markets
"""
from framework import BaseTester, TestResult, TestStatus


def test_market_quote(tester: BaseTester) -> list:
    """Test V2 unified market/quote/{market} endpoint for all markets"""
    results = []

    markets = {
        "hk": {"codes": "00700,00941", "display": "HK"},
        "cn": {"codes": "600519,000001", "display": "CN"},
        "us": {"codes": "AAPL,TSLA", "display": "US"},
    }

    for market, cfg in markets.items():
        # 1. Basic multi-code query
        resp = tester.client.v2_get_market_quote(market=market, codes=cfg["codes"])
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}
        if ok:
            ok = data.get("success") is True
        if ok:
            quote_data = data.get("data")
            ok = isinstance(quote_data, dict) and len(quote_data) > 0
        if ok:
            for code in cfg["codes"].split(","):
                code = code.strip()
                if code not in quote_data:
                    ok = False
                    break

        results.append(tester._make_result(
            f"Market Quote: {cfg['display']} (multi-code)",
            f"market_quote_{market}_basic",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"market/quote/{market}({cfg['codes']}) - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

        # 2. Fields filter
        single_code = cfg["codes"].split(",")[0].strip()
        resp2 = tester.client.v2_get_market_quote(market=market, codes=single_code, fields="name,price,chgPct")
        ok2 = resp2.success
        data2 = resp2.data if isinstance(resp2.data, dict) else {}
        if ok2:
            ok2 = data2.get("success") is True
        if ok2:
            quote_data2 = data2.get("data", {})
            ok2 = isinstance(quote_data2, dict) and single_code in quote_data2
        if ok2:
            item = quote_data2[single_code]
            ok2 = "name" in item and "price" in item and "chgPct" in item

        results.append(tester._make_result(
            f"Market Quote: {cfg['display']} (fields filter)",
            f"market_quote_{market}_fields",
            TestStatus.PASSED if ok2 else TestStatus.FAILED,
            f"market/quote/{market}({single_code}, fields=name,price,chgPct) - {'OK' if ok2 else 'FAILED'}",
            resp2.response_time_ms,
            resp2.error if not ok2 else None,
        ))

        # 3. Response structure: timestamp and message
        resp3 = tester.client.v2_get_market_quote(market=market, codes=single_code)
        ok3 = resp3.success
        data3 = resp3.data if isinstance(resp3.data, dict) else {}
        if ok3:
            ok3 = data3.get("success") is True and isinstance(data3.get("timestamp"), int)
        if ok3:
            ok3 = isinstance(data3.get("message"), str) and len(data3.get("message", "")) > 0

        results.append(tester._make_result(
            f"Market Quote: {cfg['display']} (response structure)",
            f"market_quote_{market}_structure",
            TestStatus.PASSED if ok3 else TestStatus.FAILED,
            f"market/quote/{market} structure check - {'OK' if ok3 else 'FAILED'}",
            resp3.response_time_ms,
            resp3.error if not ok3 else None,
        ))

    return results
