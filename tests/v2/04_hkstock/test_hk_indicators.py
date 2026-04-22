"""
V2 HKStock indicator tests (10 indicators)
MA, EMA, MACD, KDJ, RSI, BOLL, ATR, OBV, CCI, ADX
Endpoints: /api/v2/indicators/{indicator}?market=hk&symbol=...
"""
from config import TUSHARE_CONFIG
from framework import BaseTester, TestResult, TestStatus

HK_SYMBOLS = TUSHARE_CONFIG["hkstock"]["symbols"]

# V2 端点的单值指标: (endpoint名, 响应中值字段名, 默认查询参数)
SINGLE_VALUE_INDICATORS = {
    "sma":  {"value_field": "sma",  "params": {"period": 20}},
    "ema":  {"value_field": "ema",  "params": {"period": 20}},
    "rsi":  {"value_field": "rsi",  "params": {"period": 14}},
    "atr":  {"value_field": "atr",  "params": {"period": 14}},
    "obv":  {"value_field": "obv",  "params": {}},
    "cci":  {"value_field": "cci",  "params": {"period": 14}},
}

# V2 端点的多值指标: (endpoint名, 嵌套对象名, 期望的子字段, 默认查询参数)
MULTI_VALUE_INDICATORS = {
    "macd": {
        "nested": "macd",
        "fields": ["dif", "dea", "macd"],
        "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    },
    "kdj": {
        "nested": "kdj",
        "fields": ["k", "d", "j"],
        "params": {"fastk_period": 9, "slowk_period": 3, "slowd_period": 3},
    },
    "boll": {
        "nested": "boll",
        "fields": ["upper", "mid", "lower"],
        "params": {"period": 20, "nbdev": 2.0},
    },
    "adx": {
        "nested": "adx",
        "fields": ["adx", "plus_di", "minus_di"],
        "params": {"period": 14},
    },
}


def test_hkstock_single_value_indicators(tester: BaseTester) -> list:
    """Test HK stock single-value indicators: MA, EMA, RSI, ATR, OBV, CCI"""
    results = []

    for symbol in HK_SYMBOLS:
        tester._log(f"\n--- Testing HK single-value indicators for {symbol} ---")

        for indicator, cfg in SINGLE_VALUE_INDICATORS.items():
            resp = tester.client.get_v2_indicator(
                indicator=indicator, market="hk", symbol=symbol,
                interval="1d", **cfg["params"]
            )
            data = resp.data if isinstance(resp.data, dict) else {}
            ok = resp.success

            msg = ""

            if ok:
                value_field = cfg["value_field"]
                if value_field not in data or "times" not in data:
                    ok = False
                    msg = "missing fields"

            results.append(tester._make_result(
                f"HK Indicator: {symbol}/{indicator}",
                "hkstock_indicator_single",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{symbol}/{indicator}" if ok else f"{symbol}/{indicator}: {msg}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    return results


def test_hkstock_multi_value_indicators(tester: BaseTester) -> list:
    """Test HK stock multi-value indicators: MACD, KDJ, BOLL, ADX"""
    results = []

    for symbol in HK_SYMBOLS:
        tester._log(f"\n--- Testing HK multi-value indicators for {symbol} ---")

        for indicator, cfg in MULTI_VALUE_INDICATORS.items():
            resp = tester.client.get_v2_indicator(
                indicator=indicator, market="hk", symbol=symbol,
                interval="1d", **cfg["params"]
            )
            data = resp.data if isinstance(resp.data, dict) else {}
            ok = resp.success

            msg = ""

            if ok:
                if "times" not in data:
                    ok = False
                    msg = "missing times"
                else:
                    nested = data.get(cfg["nested"])
                    if not isinstance(nested, dict):
                        ok = False
                        msg = f"missing nested '{cfg['nested']}' object"
                    else:
                        missing = [f for f in cfg["fields"] if f not in nested]
                        if missing:
                            ok = False
                            msg = f"missing {', '.join(missing)}"
                        else:
                            msg = ""

            results.append(tester._make_result(
                f"HK Indicator: {symbol}/{indicator}",
                "hkstock_indicator_multi",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{symbol}/{indicator}" if ok else f"{symbol}/{indicator}: {msg}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    return results
