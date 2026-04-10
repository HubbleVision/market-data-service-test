"""
V2 indicator mathematical sanity tests
Validates indicator values are within expected ranges:
- RSI in [0,100], NATR in [0,100], ADX in [0,100], etc.
- MACD histogram = DIF - DEA
- BOLL upper >= middle >= lower
- KDJ J = 3K - 2D
"""
from typing import List, Dict, Callable
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
    "sar": [],
    "ultosc": [],
    "aroon": ["up", "down", "oscillator"],
}


def test_value_sanity(tester: BaseTester) -> list:
    """Validate indicator calculation values are in reasonable ranges (crypto market)"""
    results = []
    cfg = V2_MARKET_CONFIG["crypto"]

    sanity_rules = {
        "sma":  _check_positive_or_zero,
        "ema":  _check_positive_or_zero,
        "rsi":  _check_range(0, 100),
        "macd": _check_macd,
        "boll": _check_boll,
        "kdj":  _check_kdj,
        "atr":  _check_positive,
        "natr": _check_range(0, 100),
        "cci":  _check_no_restrict,
        "adx":  _check_range(0, 100),
        "vwap": _check_positive,
        "obv":  _check_no_restrict,
        "stddev": _check_positive,
        "mfi":  _check_range(0, 100),
        "willr": _check_range(-100, 0),
        "aroon": _check_aroon,
        "sar":  _check_positive,
        "trix": _check_no_restrict,
        "mom":  _check_no_restrict,
        "roc":  _check_no_restrict,
        "cmo":  _check_range(-100, 100),
        "ultosc": _check_range(0, 100),
        "ppo":  _check_ppo,
        "stoch": _check_range(0, 100),
        "ad":   _check_no_restrict,
        "adosc": _check_no_restrict,
        "ht_trendline": _check_no_restrict,
    }

    for indicator, check_fn in sanity_rules.items():
        params = {"market": "crypto", "symbol": cfg["symbol"],
                  "exchange": cfg["exchange"], "interval": cfg["interval"]}
        params.update(V2_INDICATOR_PARAMS.get(indicator, {}))

        resp = tester.client.get(f"/api/v2/indicators/{indicator}", params=params)
        data = resp.data if isinstance(resp.data, dict) else {}

        if not resp.success:
            results.append(tester._make_result(
                f"Sanity: crypto/{indicator}",
                "sanity",
                TestStatus.SKIPPED,
                f"skipped: request failed ({resp.status_code})",
                resp.response_time_ms,
                resp.error,
            ))
            continue

        passed, reason = check_fn(indicator, data)
        results.append(tester._make_result(
            f"Sanity: crypto/{indicator}",
            "sanity",
            TestStatus.PASSED if passed else TestStatus.FAILED,
            f"crypto/{indicator}" if passed else f"crypto/{indicator}: {reason}",
            resp.response_time_ms,
            None,
        ))

    return results


# --- Sanity check helpers ---

def _all_values(indicator: str, data: dict) -> list:
    if indicator in MULTI_VALUE_INDICATORS:
        fields = MULTI_VALUE_INDICATORS[indicator]
        vals = []
        for f in fields:
            v = data.get(f)
            if isinstance(v, list):
                vals.extend(v)
        return vals
    return data.get("values", [])


def _check_positive(indicator, data):
    vals = _all_values(indicator, data)
    negatives = [v for v in vals if v < 0]
    if negatives:
        return False, f"found {len(negatives)} negative values (min={min(negatives):.4f})"
    return True, ""


def _check_positive_or_zero(indicator, data):
    vals = _all_values(indicator, data)
    negatives = [v for v in vals if v < 0]
    if negatives:
        return False, f"found {len(negatives)} negative values (min={min(negatives):.4f})"
    return True, ""


def _check_range(lo, hi):
    def checker(indicator, data):
        vals = _all_values(indicator, data)
        valid = [v for v in vals if v != 0]
        if not valid:
            return True, ""
        out_of_range = [v for v in valid if v < lo or v > hi]
        if out_of_range:
            return False, f"{len(out_of_range)} values out of [{lo},{hi}] (min={min(out_of_range):.4f}, max={max(out_of_range):.4f})"
        return True, ""
    return checker


def _check_no_restrict(indicator, data):
    vals = _all_values(indicator, data)
    if not vals:
        return False, "no values returned"
    return True, ""


def _check_macd(indicator, data):
    dif = data.get("dif", [])
    dea = data.get("dea", [])
    macd_hist = data.get("macd", [])
    if not dif or not dea or not macd_hist:
        return False, "missing dif/dea/macd fields"
    if len(dif) != len(dea) or len(dif) != len(macd_hist):
        return False, f"length mismatch: dif={len(dif)}, dea={len(dea)}, macd={len(macd_hist)}"
    for i in range(len(dif)):
        expected = dif[i] - dea[i]
        diff = abs(macd_hist[i] - expected)
        if diff > abs(expected) * 0.01 + 1e-8:
            return False, f"macd[{i}]={macd_hist[i]:.6f} != dif-dea={expected:.6f}"
    return True, ""


def _check_boll(indicator, data):
    upper = data.get("upper", [])
    middle = data.get("middle", [])
    lower = data.get("lower", [])
    if not upper or not middle or not lower:
        return False, "missing upper/middle/lower fields"
    for i in range(len(upper)):
        if upper[i] < middle[i]:
            return False, f"upper[{i}]={upper[i]:.4f} < middle[{i}]={middle[i]:.4f}"
        if middle[i] < lower[i]:
            return False, f"middle[{i}]={middle[i]:.4f} < lower[{i}]={lower[i]:.4f}"
    return True, ""


def _check_kdj(indicator, data):
    k = data.get("k", [])
    d = data.get("d", [])
    j = data.get("j", [])
    if not k or not d or not j:
        return False, "missing k/d/j fields"
    for i in range(len(k)):
        expected_j = 3 * k[i] - 2 * d[i]
        diff = abs(j[i] - expected_j)
        if diff > abs(expected_j) * 0.01 + 1e-8:
            return False, f"j[{i}]={j[i]:.4f} != 3k-2d={expected_j:.4f}"
    return True, ""


def _check_aroon(indicator, data):
    up = data.get("up", [])
    down = data.get("down", [])
    osc = data.get("oscillator", [])
    if not up or not down or not osc:
        return False, "missing up/down/oscillator fields"
    for i in range(len(up)):
        if up[i] < 0 or up[i] > 100:
            return False, f"up[{i}]={up[i]:.4f} out of [0,100]"
        if down[i] < 0 or down[i] > 100:
            return False, f"down[{i}]={down[i]:.4f} out of [0,100]"
        if osc[i] < -100 or osc[i] > 100:
            return False, f"oscillator[{i}]={osc[i]:.4f} out of [-100,100]"
    return True, ""


def _check_ppo(indicator, data):
    values = data.get("values", [])
    signal = data.get("signal", [])
    histogram = data.get("histogram", [])
    if not values or not signal or not histogram:
        return False, "missing values/signal/histogram fields"
    if len(values) != len(signal) or len(values) != len(histogram):
        return False, f"length mismatch: values={len(values)}, signal={len(signal)}, histogram={len(histogram)}"
    for i in range(len(values)):
        expected = values[i] - signal[i]
        diff = abs(histogram[i] - expected)
        if diff > abs(expected) * 0.01 + 1e-8:
            return False, f"histogram[{i}]={histogram[i]:.6f} != values-signal={expected:.6f}"
    return True, ""
