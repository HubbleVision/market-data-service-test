"""
V2 single-value indicator tests (18 indicators)
SMA, EMA, RSI, ATR, NATR, CCI, VWAP, MFI, WILLR, STDDEV,
TRIX, MOM, ROC, CMO, OBV, AD, HT_TRENDLINE
"""
from typing import List
from framework import BaseTester, TestResult, TestStatus
from config import V2_INDICATORS, V2_INDICATOR_PARAMS, V2_MARKET_CONFIG

SINGLE_VALUE_INDICATORS = [
    "sma", "ema", "rsi", "atr", "natr", "cci", "vwap", "mfi", "willr",
    "stddev", "trix", "mom", "roc", "cmo", "obv", "ad", "ht_trendline",
]


def test_single_value_indicators(tester: BaseTester) -> list:
    """Test all 18 single-value indicators on crypto and cn markets"""
    results = []

    for market, cfg in V2_MARKET_CONFIG.items():
        tester._log(f"\n--- Testing single-value indicators for market: {market} ---")

        for indicator in SINGLE_VALUE_INDICATORS:
            params = {"market": market, "symbol": cfg["symbol"], "interval": cfg["interval"]}
            if cfg.get("exchange"):
                params["exchange"] = cfg["exchange"]
            params.update(V2_INDICATOR_PARAMS.get(indicator, {}))

            resp = tester.client.get(f"/api/v2/indicators/{indicator}", params=params)
            data = resp.data if isinstance(resp.data, dict) else {}
            ok = resp.success

            if ok:
                if "values" not in data or "times" not in data:
                    ok = False

            results.append(tester._make_result(
                f"Single: {market}/{indicator}",
                "indicator_single",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{market}/{indicator}" if ok else f"{market}/{indicator}: missing values/times",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    return results
