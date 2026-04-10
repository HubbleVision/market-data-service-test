"""
V2 new indicators tests (26 indicators added in 指标补充)
Batch 1 - Moving Averages (single-value): wma, dema, tema, trima, kama, t3, midpoint
Batch 2 - Momentum/Oscillators (single-value): apo, rocr, bop
Batch 2 - Momentum/Oscillators (multi-value): stochf, adxr
Batch 2 - Momentum/Oscillators (single-value): stochrsi
Batch 3 - ADX/ATR sub-indicators (single-value): dx, plus_dm, minus_dm, plus_di, minus_di, trange, aroonosc
Batch 4 - Hilbert Transform (single-value): ht_dcperiod, ht_dcphase
Batch 4 - Hilbert Transform (multi-value): ht_sine, ht_phasor
Batch 4 - Hilbert Transform (single-value): ht_trendmode
Batch 5 - MACD Extension (multi-value): macdext
Batch 6 - Price (single-value): midprice
"""
from framework import BaseTester, TestResult, TestStatus
from config import V2_MARKET_CONFIG

# New indicator params (key=indicator, value=query param dict)
NEW_INDICATOR_PARAMS = {
    # Batch 1: Moving Averages
    "wma":           {"period": 20},
    "dema":          {"period": 20},
    "tema":          {"period": 20},
    "trima":         {"period": 20},
    "kama":          {"period": 10},
    "t3":            {"period": 20, "vfactor": 0.7},
    "midpoint":      {"period": 14},
    # Batch 2: Momentum/Oscillators
    "stochf":        {"k_period": 14, "fastd_period": 3},
    "stochrsi":      {"period": 14, "fastk_period": 5, "fastd_period": 3},
    "apo":           {"fast_period": 12, "slow_period": 26},
    "rocr":          {"period": 14},
    "bop":           {},
    "adxr":          {"period": 14},
    # Batch 3: ADX/ATR sub-indicators
    "dx":            {"period": 14},
    "plus_dm":       {"period": 14},
    "minus_dm":      {"period": 14},
    "plus_di":       {"period": 14},
    "minus_di":      {"period": 14},
    "trange":        {"period": 14},
    "aroonosc":      {"period": 14},
    # Batch 4: Hilbert Transform
    "ht_sine":       {},
    "ht_trendmode":  {},
    "ht_dcperiod":   {},
    "ht_dcphase":    {},
    "ht_phasor":     {},
    # Batch 5: MACD Extension
    "macdext":       {"fast_period": 12, "slow_period": 26, "signal_period": 9, "matype": 1},
    # Batch 6: Price
    "midprice":      {"period": 14},
}

# Single-value indicators: expect "values" and "times" in response
SINGLE_VALUE_INDICATORS = [
    "wma", "dema", "tema", "trima", "kama", "t3", "midpoint",
    "stochrsi", "apo", "rocr", "bop",
    "dx", "plus_dm", "minus_dm", "plus_di", "minus_di", "trange", "aroonosc",
    "ht_dcperiod", "ht_dcphase", "ht_trendmode",
    "midprice",
]

# Multi-value indicators: expect "times" + specific output fields
MULTI_VALUE_INDICATORS = {
    "stochf":  ["fastk", "fastd"],
    "adxr":    ["adxr"],
    "ht_sine": ["sine", "leadsine"],
    "ht_phasor": ["inphase", "quadrature"],
    "macdext": ["dif", "dea", "macd"],
}


def test_new_single_value_indicators(tester: BaseTester) -> list:
    """Test all new single-value indicators on crypto and cn markets"""
    results = []

    for market, cfg in V2_MARKET_CONFIG.items():
        tester._log(f"\n--- Testing new single-value indicators for market: {market} ---")

        for indicator in SINGLE_VALUE_INDICATORS:
            params = {"market": market, "symbol": cfg["symbol"], "interval": cfg["interval"]}
            if cfg.get("exchange"):
                params["exchange"] = cfg["exchange"]
            params.update(NEW_INDICATOR_PARAMS.get(indicator, {}))

            resp = tester.client.get(f"/api/v2/indicators/{indicator}", params=params)
            data = resp.data if isinstance(resp.data, dict) else {}
            ok = resp.success

            if ok:
                if "values" not in data or "times" not in data:
                    ok = False

            results.append(tester._make_result(
                f"New Single: {market}/{indicator}",
                "indicator_new_single",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{market}/{indicator}" if ok else f"{market}/{indicator}: missing values/times",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    return results


def test_new_multi_value_indicators(tester: BaseTester) -> list:
    """Test all new multi-value indicators on crypto and cn markets"""
    results = []

    for market, cfg in V2_MARKET_CONFIG.items():
        tester._log(f"\n--- Testing new multi-value indicators for market: {market} ---")

        for indicator, expected_fields in MULTI_VALUE_INDICATORS.items():
            params = {"market": market, "symbol": cfg["symbol"], "interval": cfg["interval"]}
            if cfg.get("exchange"):
                params["exchange"] = cfg["exchange"]
            params.update(NEW_INDICATOR_PARAMS.get(indicator, {}))

            resp = tester.client.get(f"/api/v2/indicators/{indicator}", params=params)
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

            results.append(tester._make_result(
                f"New Multi: {market}/{indicator}",
                "indicator_new_multi",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{market}/{indicator}" if ok else f"{market}/{indicator}: {msg}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    return results


def test_new_indicators_with_custom_params(tester: BaseTester) -> list:
    """Test new indicators with non-default parameters"""
    results = []

    test_cases = [
        # (indicator, params, description)
        ("t3", {"period": 5, "vfactor": 0.5}, "T3 short period low vfactor"),
        ("t3", {"period": 50, "vfactor": 0.8}, "T3 long period high vfactor"),
        ("kama", {"period": 5}, "KAMA short period"),
        ("kama", {"period": 30}, "KAMA long period"),
        ("macdext", {"fast_period": 5, "slow_period": 34, "signal_period": 5, "matype": 0},
         "MACDEXT SMA mode"),
        ("macdext", {"fast_period": 12, "slow_period": 26, "signal_period": 9, "matype": 2},
         "MACDEXT WMA mode"),
        ("stochf", {"k_period": 5, "fastd_period": 5}, "STOCHF short periods"),
        ("stochrsi", {"period": 10, "fastk_period": 3, "fastd_period": 3}, "STOCHRSI short RSI"),
        ("midprice", {"period": 5}, "MIDPRICE short period"),
        ("midprice", {"period": 50}, "MIDPRICE long period"),
    ]

    for indicator, extra_params, desc in test_cases:
        cfg = V2_MARKET_CONFIG["crypto"]
        params = {
            "market": "crypto",
            "symbol": cfg["symbol"],
            "interval": cfg["interval"],
            "exchange": cfg["exchange"],
        }
        params.update(extra_params)

        resp = tester.client.get(f"/api/v2/indicators/{indicator}", params=params)
        ok = resp.success
        data = resp.data if isinstance(resp.data, dict) else {}

        if ok and "values" not in data and "times" not in data:
            ok = False

        results.append(tester._make_result(
            f"New Params: {desc}",
            "indicator_new_params",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{indicator} custom params - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
