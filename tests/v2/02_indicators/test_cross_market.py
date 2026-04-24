"""
V2 indicator cross-market coverage tests
Tests that crypto + cn return 200, hk + us return 501
"""
from framework import BaseTester, TestResult, TestStatus
from config import V2_INDICATORS, V2_INDICATOR_PARAMS, V2_MARKET_CONFIG


def test_cross_market(tester: BaseTester) -> list:
    """Test all 27 indicators across all markets; hk/us expected 501, crypto uses separate endpoint"""
    results = []

    # Add hk/us config stubs (expected 501)
    all_markets = {
        **V2_MARKET_CONFIG,
        "hk": {"symbol": "00700.HK", "exchange": "", "interval": "1d"},
        "us": {"symbol": "AAPL", "exchange": "", "interval": "1d"},
    }

    for market, cfg in all_markets.items():
        tester._log(f"\n--- Testing cross-market: {market} ---")
        is_stub = market in ("hk", "us")

        for indicator in V2_INDICATORS:
            params = {"symbol": cfg["symbol"], "interval": cfg["interval"]}
            if cfg.get("exchange"):
                params["exchange"] = cfg["exchange"]
            params.update(V2_INDICATOR_PARAMS.get(indicator, {}))

            # crypto uses separate endpoint /api/v2/crypto/indicators/{indicator}
            # cn uses /api/v2/indicators/{indicator} with market param
            # hk/us use /api/v2/indicators/{indicator} (expected 501)
            if market == "crypto":
                endpoint = f"/api/v2/crypto/indicators/{indicator}"
                # crypto endpoint doesn't need market param, needs exchange
                if not cfg.get("exchange"):
                    params["exchange"] = "binance"
            else:
                endpoint = f"/api/v2/indicators/{indicator}"
                params["market"] = market

            resp = tester.client.get(endpoint, params=params)

            if is_stub:
                ok = resp.status_code == 501
                msg = f"{market}/{indicator}" if ok else f"{market}/{indicator}: expected 501, got {resp.status_code}"
                results.append(tester._make_result(
                    f"CrossMarket: {market}/{indicator}",
                    "cross_market",
                    TestStatus.PASSED if ok else TestStatus.FAILED,
                    msg, resp.response_time_ms,
                    resp.error if not ok else None,
                ))
            else:
                ok = resp.success
                msg = f"{market}/{indicator}" if ok else f"{market}/{indicator}: HTTP {resp.status_code}"
                results.append(tester._make_result(
                    f"CrossMarket: {market}/{indicator}",
                    "cross_market",
                    TestStatus.PASSED if ok else TestStatus.FAILED,
                    msg, resp.response_time_ms,
                    resp.error if not ok else None,
                ))

    return results
