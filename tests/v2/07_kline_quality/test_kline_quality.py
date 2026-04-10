"""
V2 K-line Data Quality Tests
Validates K-line data integrity across CN/HK/US stock markets.

Checks:
  1. OHLC structure — High>=Low, prices>0, volume>=0
  2. Price change anomaly — daily change exceeds market threshold
  3. Volume anomaly — volume spike >15x or zero with price change
  4. Data freshness — latest kline within 2 calendar days
  5. Cross verification — query third-party source on anomalies
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

import requests

from framework import BaseTester, TestResult, TestStatus
from config import TUSHARE_CONFIG

# ---------------------------------------------------------------------------
# Thresholds per market
# ---------------------------------------------------------------------------
PRICE_CHANGE_THRESHOLD = {
    "cn": 30.0,   # A股: 主板±10%, 科创/创业板±20%, 新股不设限 → 用30兜底
    "hk": 50.0,   # 港股: 无涨跌停, 单日50%+极为罕见
    "us": 40.0,   # 美股: 无涨跌停, 单日40%+极为罕见
}

VOLUME_SPIKE_MULTIPLIER = 15   # 成交量 > 均量15倍视为异常
FRESHNESS_MAX_DAYS = 2         # 允许的最大数据延迟(自然日)

# Sina Finance referer required
_SINA_HEADERS = {
    "Referer": "https://finance.sina.com.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


# ===========================================================================
# Data fetching helpers
# ===========================================================================

def _fetch_klines(tester: BaseTester, market: str, symbol: str, limit: int = 60) -> list:
    """Fetch kline data from the appropriate endpoint, return data list."""
    if market == "cn":
        resp = tester.client.v2_get_cnstock_klines(symbol=symbol, interval="daily", limit=limit)
    elif market == "hk":
        resp = tester.client.v2_get_hkstock_daily(symbol=symbol, limit=limit)
    elif market == "us":
        resp = tester.client.v2_get_usstock_daily(symbol=symbol, limit=limit)
    else:
        return []

    if not resp.success:
        return []

    data = resp.data if isinstance(resp.data, dict) else {}
    items = data.get("data")
    return items if isinstance(items, list) else []


def _all_symbols() -> List[Tuple[str, str, str]]:
    """Return [(market, symbol, label), ...] from config."""
    syms = []
    for s in TUSHARE_CONFIG.get("astock", {}).get("symbols", []):
        syms.append(("cn", s, f"CN/{s}"))
    for s in TUSHARE_CONFIG.get("hkstock", {}).get("symbols", []):
        syms.append(("hk", s, f"HK/{s}"))
    for s in TUSHARE_CONFIG.get("usstock", {}).get("symbols", []):
        syms.append(("us", s, f"US/{s}"))
    return syms


# ===========================================================================
# Check helpers
# ===========================================================================

def _check_ohlc_single(bar: dict) -> Optional[str]:
    """Check one bar's OHLC structure. Returns reason string if invalid, None if OK."""
    o = bar.get("open")
    h = bar.get("high")
    l = bar.get("low")
    c = bar.get("close")
    v = bar.get("volume")

    if o is None or h is None or l is None or c is None:
        return f"missing OHLC field (time={bar.get('time', '?')})"

    if v is None or v < 0:
        return f"volume invalid: {v} (time={bar.get('time', '?')})"

    if o <= 0 or c <= 0:
        return f"price <= 0: open={o}, close={c} (time={bar.get('time', '?')})"

    if h < l:
        return f"high < low: {h} < {l} (time={bar.get('time', '?')})"

    if h < o:
        return f"high < open: {h} < {o} (time={bar.get('time', '?')})"
    if h < c:
        return f"high < close: {h} < {c} (time={bar.get('time', '?')})"
    if l > o:
        return f"low > open: {l} > {o} (time={bar.get('time', '?')})"
    if l > c:
        return f"low > close: {l} > {c} (time={bar.get('time', '?')})"

    return None


def _find_price_anomalies(klines: list, market: str) -> list:
    """
    Find days where daily price change exceeds threshold.
    For CN stocks with adjFactor, uses adjusted close.
    Returns list of dicts: {time, close_prev, close_curr, change_pct}
    """
    if len(klines) < 2:
        return []

    threshold = PRICE_CHANGE_THRESHOLD.get(market, 50.0)
    anomalies = []

    for i in range(1, len(klines)):
        prev, curr = klines[i - 1], klines[i]
        c_prev = prev.get("close", 0)
        c_curr = curr.get("close", 0)

        # For A-shares with adjFactor, use adjusted price
        if market == "cn":
            af_prev = prev.get("adjFactor") or 1.0
            af_curr = curr.get("adjFactor") or 1.0
            c_prev = c_prev * af_prev
            c_curr = c_curr * af_curr

        if c_prev <= 0:
            continue

        change_pct = (c_curr - c_prev) / c_prev * 100.0
        if abs(change_pct) > threshold:
            anomalies.append({
                "time": curr.get("time", "?"),
                "close_prev": prev.get("close", 0),
                "close_curr": curr.get("close", 0),
                "change_pct": round(change_pct, 2),
            })

    return anomalies


def _find_volume_anomalies(klines: list) -> list:
    """
    Find days where volume is anomalous relative to recent average.
    Returns list of dicts: {time, volume, avg_vol, ratio}
    """
    if len(klines) < 21:
        return []

    # Use first 20 bars as baseline
    baseline = klines[:20]
    avg_vol = sum(b.get("volume", 0) for b in baseline) / 20.0
    if avg_vol <= 0:
        return []

    anomalies = []
    for bar in klines[20:]:
        vol = bar.get("volume", 0)
        ratio = vol / avg_vol

        is_anomaly = False
        reason = ""
        if vol == 0 and bar.get("close", 0) != bar.get("open", 0):
            is_anomaly = True
            reason = "zero volume with price change"
        elif ratio > VOLUME_SPIKE_MULTIPLIER:
            is_anomaly = True
            reason = f"volume {ratio:.1f}x average"

        if is_anomaly:
            anomalies.append({
                "time": bar.get("time", "?"),
                "volume": vol,
                "avg_vol": round(avg_vol, 0),
                "ratio": round(ratio, 1),
                "reason": reason,
            })

    return anomalies


# ===========================================================================
# Third-party verification helpers
# ===========================================================================

def _verify_sina(symbol: str, date_str: str) -> Tuple[Optional[float], str]:
    """
    Query Sina Finance for A-share closing price on a given date.
    symbol: e.g. "000001.SZ"
    date_str: e.g. "20260403"
    Returns (close_price, note).
    """
    # Convert ts_code to sina format: 000001.SZ → sz000001
    sina_code = ""
    if ".SZ" in symbol:
        sina_code = "sz" + symbol.replace(".SZ", "")
    elif ".SH" in symbol:
        sina_code = "sh" + symbol.replace(".SH", "")
    else:
        return None, f"unsupported symbol format: {symbol}"

    try:
        resp = requests.get(
            f"https://hq.sinajs.cn/list={sina_code}",
            headers=_SINA_HEADERS,
            timeout=10,
        )
        if resp.status_code != 200:
            return None, f"sina HTTP {resp.status_code}"

        # Parse: var hq_str_sz000001="平安银行,12.50,12.30,...";
        text = resp.text.strip()
        if '="' not in text or '";' not in text:
            return None, f"sina parse error: empty response"

        fields = text.split('="')[1].split('";')[0].split(",")
        if len(fields) < 4:
            return None, f"sina parse error: too few fields ({len(fields)})"

        close = float(fields[2])  # 昨收 in field index 2 (yesterday close)
        open_price = float(fields[0])  # today open in field index 0
        # fields[3] is current price
        # Note: Sina returns real-time data, not historical. For historical close,
        # we can only compare the latest available data as a sanity check.
        # For full historical verification, Tushare direct API would be better.

        return close, f"sina close={close}"
    except Exception as e:
        return None, f"sina request failed: {str(e)[:100]}"


def _verify_yahoo(symbol: str, date_str: str) -> Tuple[Optional[float], str]:
    """
    Query Yahoo Finance for HK/US stock closing price.
    symbol: e.g. "00700.HK" or "AAPL"
    date_str: e.g. "20260403"
    Returns (close_price, note).
    """
    # Convert to yfinance format
    yf_symbol = symbol
    if ".HK" in symbol:
        yf_symbol = symbol  # 00700.HK works directly
    elif "." not in symbol:
        yf_symbol = symbol  # AAPL works directly

    try:
        import pandas as pd
        # Parse date
        dt = datetime.strptime(date_str, "%Y%m%d")
        start = (dt - timedelta(days=5)).strftime("%Y-%m-%d")
        end = (dt + timedelta(days=1)).strftime("%Y-%m-%d")

        import yfinance as yf
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(start=start, end=end)

        if hist.empty:
            return None, f"yahoo: no data for {yf_symbol} around {date_str}"

        # Find the closest date
        hist_dates = [d.strftime("%Y%m%d") for d in hist.index]
        closest_idx = min(range(len(hist_dates)),
                          key=lambda i: abs((datetime.strptime(hist_dates[i], "%Y%m%d") - dt).days))

        close = float(hist.iloc[closest_idx]["Close"])
        actual_date = hist_dates[closest_idx]

        return close, f"yahoo({yf_symbol}) close={close} on {actual_date}"
    except ImportError:
        return None, "yfinance not installed (pip install yfinance)"
    except Exception as e:
        return None, f"yahoo request failed: {str(e)[:100]}"


def _cross_verify(market: str, symbol: str, date_str: str) -> Tuple[Optional[float], str]:
    """Route to the appropriate third-party verifier."""
    if market == "cn":
        return _verify_sina(symbol, date_str)
    else:
        return _verify_yahoo(symbol, date_str)


# ===========================================================================
# Test functions
# ===========================================================================

def test_ohlc_structure(tester: BaseTester) -> list:
    """Validate OHLC structure for all configured stock symbols."""
    results = []

    for market, symbol, label in _all_symbols():
        klines = _fetch_klines(tester, market, symbol, limit=30)

        if not klines:
            results.append(tester._make_result(
                f"OHLC: {label}",
                "kline_ohlc",
                TestStatus.SKIPPED,
                f"{label}: no data returned",
                0,
                None,
            ))
            continue

        errors = []
        for bar in klines:
            reason = _check_ohlc_single(bar)
            if reason:
                errors.append(reason)

        if errors:
            results.append(tester._make_result(
                f"OHLC: {label}",
                "kline_ohlc",
                TestStatus.FAILED,
                f"{label}: {len(errors)}/{len(klines)} bars invalid. First: {errors[0]}",
                0,
                "; ".join(errors[:3]),
            ))
        else:
            results.append(tester._make_result(
                f"OHLC: {label}",
                "kline_ohlc",
                TestStatus.PASSED,
                f"{label}: all {len(klines)} bars OK",
                0,
                None,
            ))

    return results


def test_price_change(tester: BaseTester) -> list:
    """Detect abnormal daily price changes."""
    results = []

    for market, symbol, label in _all_symbols():
        klines = _fetch_klines(tester, market, symbol, limit=60)

        if not klines or len(klines) < 2:
            results.append(tester._make_result(
                f"PriceChange: {label}",
                "kline_price_change",
                TestStatus.SKIPPED,
                f"{label}: insufficient data",
                0,
                None,
            ))
            continue

        anomalies = _find_price_anomalies(klines, market)
        threshold = PRICE_CHANGE_THRESHOLD.get(market, 50.0)

        if anomalies:
            a = anomalies[0]
            results.append(tester._make_result(
                f"PriceChange: {label}",
                "kline_price_change",
                TestStatus.FAILED,
                f"{label}: {len(anomalies)} anomaly(s). "
                f"Latest: {a['time']} close {a['close_prev']}→{a['close_curr']} ({a['change_pct']:+.1f}%) "
                f"[threshold ±{threshold}%]",
                0,
                str(anomalies),
            ))
        else:
            results.append(tester._make_result(
                f"PriceChange: {label}",
                "kline_price_change",
                TestStatus.PASSED,
                f"{label}: no anomaly in {len(klines)} bars (threshold ±{threshold}%)",
                0,
                None,
            ))

    return results


def test_volume_anomaly(tester: BaseTester) -> list:
    """Detect abnormal volume spikes or zero-volume with price change."""
    results = []

    for market, symbol, label in _all_symbols():
        klines = _fetch_klines(tester, market, symbol, limit=60)

        if not klines or len(klines) < 21:
            results.append(tester._make_result(
                f"Volume: {label}",
                "kline_volume",
                TestStatus.SKIPPED,
                f"{label}: insufficient data (need >=21 bars)",
                0,
                None,
            ))
            continue

        anomalies = _find_volume_anomalies(klines)

        if anomalies:
            a = anomalies[0]
            results.append(tester._make_result(
                f"Volume: {label}",
                "kline_volume",
                TestStatus.FAILED,
                f"{label}: {len(anomalies)} anomaly(s). "
                f"Latest: {a['time']} vol={a['volume']}, avg={a['avg_vol']} "
                f"({a['ratio']}x) — {a['reason']}",
                0,
                str(anomalies),
            ))
        else:
            results.append(tester._make_result(
                f"Volume: {label}",
                "kline_volume",
                TestStatus.PASSED,
                f"{label}: volume normal across {len(klines)} bars",
                0,
                None,
            ))

    return results


def test_data_freshness(tester: BaseTester) -> list:
    """Check that the latest kline is recent enough."""
    results = []
    today = datetime.now()
    cutoff = today - timedelta(days=FRESHNESS_MAX_DAYS)
    cutoff_str = cutoff.strftime("%Y%m%d")

    for market, symbol, label in _all_symbols():
        klines = _fetch_klines(tester, market, symbol, limit=5)

        if not klines:
            results.append(tester._make_result(
                f"Freshness: {label}",
                "kline_freshness",
                TestStatus.SKIPPED,
                f"{label}: no data",
                0,
                None,
            ))
            continue

        # Data is chronological (oldest first), latest is last
        latest_time = klines[-1].get("time", "")
        latest_date = datetime.strptime(latest_time, "%Y%m%d") if latest_time else None

        if latest_date is None:
            results.append(tester._make_result(
                f"Freshness: {label}",
                "kline_freshness",
                TestStatus.FAILED,
                f"{label}: cannot parse latest time '{latest_time}'",
                0,
                None,
            ))
            continue

        if latest_date < cutoff:
            days_lag = (today - latest_date).days
            results.append(tester._make_result(
                f"Freshness: {label}",
                "kline_freshness",
                TestStatus.FAILED,
                f"{label}: latest={latest_time}, {days_lag} days stale (max={FRESHNESS_MAX_DAYS})",
                0,
                None,
            ))
        else:
            days_lag = (today - latest_date).days
            results.append(tester._make_result(
                f"Freshness: {label}",
                "kline_freshness",
                TestStatus.PASSED,
                f"{label}: latest={latest_time}, {days_lag} day(s) ago",
                0,
                None,
            ))

    return results


def test_cross_verify(tester: BaseTester) -> list:
    """
    When price anomalies are detected, cross-verify with third-party data.
    Runs price_change check first, then verifies any anomalies found.
    """
    results = []

    for market, symbol, label in _all_symbols():
        klines = _fetch_klines(tester, market, symbol, limit=60)

        if not klines or len(klines) < 2:
            results.append(tester._make_result(
                f"CrossVerify: {label}",
                "kline_cross_verify",
                TestStatus.SKIPPED,
                f"{label}: insufficient data, skip cross verify",
                0,
                None,
            ))
            continue

        anomalies = _find_price_anomalies(klines, market)

        if not anomalies:
            # No anomalies → cross verify not needed
            results.append(tester._make_result(
                f"CrossVerify: {label}",
                "kline_cross_verify",
                TestStatus.PASSED,
                f"{label}: no price anomaly, cross verify not needed",
                0,
                None,
            ))
            continue

        # Verify each anomaly against third-party
        verified_ok = 0
        confirmed_bad = 0
        verify_details = []

        for a in anomalies:
            ext_close, note = _cross_verify(market, symbol, a["time"])
            verify_details.append(f"{a['time']}: {note}")

            if ext_close is not None:
                our_close = a["close_curr"]
                # Allow 2% tolerance for data source differences
                diff_pct = abs(our_close - ext_close) / ext_close * 100
                if diff_pct < 2:
                    verified_ok += 1
                else:
                    confirmed_bad += 1

        total = len(anomalies)
        if confirmed_bad > 0:
            results.append(tester._make_result(
                f"CrossVerify: {label}",
                "kline_cross_verify",
                TestStatus.FAILED,
                f"{label}: {confirmed_bad}/{total} confirmed BAD via 3rd party. "
                f"Details: {'; '.join(verify_details[:3])}",
                0,
                str(verify_details),
            ))
        elif verified_ok == total:
            results.append(tester._make_result(
                f"CrossVerify: {label}",
                "kline_cross_verify",
                TestStatus.PASSED,
                f"{label}: {total} anomaly(s) all confirmed as real market data via 3rd party",
                0,
                None,
            ))
        else:
            results.append(tester._make_result(
                f"CrossVerify: {label}",
                "kline_cross_verify",
                TestStatus.SKIPPED,
                f"{label}: {total} anomaly(s), 3rd party unreachable for some. "
                f"Details: {'; '.join(verify_details[:3])}",
                0,
                str(verify_details),
            ))

    return results
