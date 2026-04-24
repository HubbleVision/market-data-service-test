"""
V2 Indicator parameter validation tests
Validates: market required, market enum, crypto requires exchange, normal requests
"""
from framework import BaseTester, TestResult, TestStatus
from config import V2_MARKET_CONFIG


def test_validation(tester: BaseTester) -> list:
    """Validate market required, enum, crypto needs exchange, normal requests"""
    results = []

    # Use CN market symbol from config for validation tests
    cn_symbol = V2_MARKET_CONFIG["cn"]["symbol"]

    # 1. Missing market -> 422
    resp = tester.client.get("/api/v2/indicators/sma", params={
        "symbol": cn_symbol, "interval": "1d"
    })
    results.append(tester._make_result(
        "Validation: missing market",
        "validation",
        TestStatus.PASSED if resp.status_code == 422 else TestStatus.FAILED,
        f"Expected 422, got {resp.status_code}",
        resp.response_time_ms,
        resp.error,
    ))

    # 2. Invalid market value -> 422
    resp = tester.client.get("/api/v2/indicators/sma", params={
        "market": "invalid", "symbol": cn_symbol, "interval": "1d"
    })
    results.append(tester._make_result(
        "Validation: invalid market value",
        "validation",
        TestStatus.PASSED if resp.status_code == 422 else TestStatus.FAILED,
        f"Expected 422, got {resp.status_code}",
        resp.response_time_ms,
        resp.error,
    ))

    # 3. Crypto without exchange -> 400 (using crypto-specific endpoint)
    resp = tester.client.get("/api/v2/crypto/indicators/sma", params={
        "symbol": "BTCUSDT", "interval": "1d"
        # note: no exchange param, should fail
    })
    results.append(tester._make_result(
        "Validation: crypto without exchange",
        "validation",
        TestStatus.PASSED if resp.status_code == 400 else TestStatus.FAILED,
        f"Expected 400, got {resp.status_code}",
        resp.response_time_ms,
        resp.error,
    ))

    # 4. Crypto + cn normal requests -> 200
    # Crypto uses /api/v2/crypto/indicators/, cn uses /api/v2/indicators/
    for market in ("crypto", "cn"):
        cfg = V2_MARKET_CONFIG[market]
        params = {"symbol": cfg["symbol"], "interval": cfg["interval"]}
        if cfg.get("exchange"):
            params["exchange"] = cfg["exchange"]

        if market == "crypto":
            endpoint = "/api/v2/crypto/indicators/sma"
            if not cfg.get("exchange"):
                params["exchange"] = "binance"
        else:
            endpoint = "/api/v2/indicators/sma"
            params["market"] = market

        resp = tester.client.get(endpoint, params=params)
        results.append(tester._make_result(
            f"Validation: {market} normal request",
            "validation",
            TestStatus.PASSED if resp.status_code == 200 else TestStatus.FAILED,
            f"market={market}, Expected 200, got {resp.status_code}",
            resp.response_time_ms,
            resp.error,
        ))

    return results
