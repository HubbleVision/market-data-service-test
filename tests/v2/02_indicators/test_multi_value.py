"""
V2 multi-value indicator tests (9 indicators)
MACD, BOLL, KDJ, ADX, PPO, SAR, STOCH, ULTOSC, ADOSC
"""
from framework import BaseTester, TestResult, TestStatus
from config import V2_INDICATOR_PARAMS, V2_MARKET_CONFIG

MULTI_VALUE_INDICATORS = {
    "macd": ["dif", "dea", "macd"],
    "boll": ["upper", "middle", "lower"],
    "kdj": ["k", "d", "j"],
    "adx": ["adx", "pdi", "mdi"],
    "ppo": ["values", "signal", "histogram"],
    "stoch": ["k", "d"],
    "adosc": ["values", "fast_period", "slow_period"],
    # SAR, ULTOSC may have different response structure - validate basic response
    "sar": [],
    "ultosc": [],
}


def test_multi_value_indicators(tester: BaseTester) -> list:
    """Test all multi-value indicators on crypto and cn markets"""
    results = []

    for market, cfg in V2_MARKET_CONFIG.items():
        tester._log(f"\n--- Testing multi-value indicators for market: {market} ---")

        for indicator, expected_fields in MULTI_VALUE_INDICATORS.items():
            params = {"symbol": cfg["symbol"], "interval": cfg["interval"]}
            if cfg.get("exchange"):
                params["exchange"] = cfg["exchange"]
            params.update(V2_INDICATOR_PARAMS.get(indicator, {}))

            # crypto uses separate endpoint /api/v2/crypto/indicators/{indicator}
            # cn uses /api/v2/indicators/{indicator} with market param
            if market == "crypto":
                endpoint = f"/api/v2/crypto/indicators/{indicator}"
                if not cfg.get("exchange"):
                    params["exchange"] = "binance"
            else:
                endpoint = f"/api/v2/indicators/{indicator}"
                params["market"] = market

            resp = tester.client.get(endpoint, params=params)
            data = resp.data if isinstance(resp.data, dict) else {}
            ok = resp.success

            msg = ""

            if ok:
                if "times" not in data:
                    ok = False
                    msg = "missing times"
                elif expected_fields:
                    missing = [f for f in expected_fields if f not in data]
                    if missing:
                        ok = False
                        msg = f"missing {', '.join(missing)}"
                    else:
                        msg = ""
                else:
                    msg = ""

            results.append(tester._make_result(
                f"Multi: {market}/{indicator}",
                "indicator_multi",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{market}/{indicator}" if ok else f"{market}/{indicator}: {msg}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    return results
