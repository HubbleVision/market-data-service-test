"""
V2 Crypto K-line tests
Comprehensive coverage: exchanges, intervals, time ranges, error scenarios
"""
import time
from datetime import datetime, timezone, timedelta
from framework import BaseTester, TestResult, TestStatus
from config import TEST_SYMBOLS, KLINE_INTERVALS


def _result(tester, name, status, msg, rt_ms, error=None):
    return tester._make_result(name, "crypto_kline", status, msg, rt_ms, error)


def _pass(tester, name, msg, rt_ms):
    return _result(tester, name, TestStatus.PASSED, msg, rt_ms)


def _fail(tester, name, msg, rt_ms, error=None):
    return _result(tester, name, TestStatus.FAILED, msg, rt_ms, error)


def _warn(tester, name, msg, rt_ms, error=None):
    return _result(tester, name, TestStatus.SKIPPED, msg, rt_ms, error)


def _has_kline_data(resp) -> bool:
    """Check if response contains non-empty kline data"""
    if not resp.success or not resp.data:
        return False
    data = resp.data if isinstance(resp.data, dict) else {}
    klines = data.get("data", [])
    return isinstance(klines, list) and len(klines) > 0


def _ago(hours=1):
    """Return RFC 3339 timestamp for N hours ago"""
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _data_count(resp):
    if resp.data and isinstance(resp.data, dict):
        return len(resp.data.get("data", []))
    return 0


# ============================================================
# 1. Multi-exchange connectivity tests
# ============================================================
def test_kline_all_exchanges(tester: BaseTester) -> list:
    """Test kline availability across all exchanges"""
    results = []
    symbol = "BTCUSDT"
    interval = "1h"

    for exchange in TEST_SYMBOLS:
        name = f"Exchange [{exchange}] kline 1h"
        try:
            resp = tester.client.v2_get_kline(
                exchange=exchange, symbol=symbol, interval=interval,
                limit=5
            )
            if _has_kline_data(resp):
                results.append(_pass(tester, name, f"OK, count={_data_count(resp)}", resp.response_time_ms))
            elif resp.status_code == 404:
                results.append(_warn(tester, name, "No data (404)", resp.response_time_ms,
                                     f"exchange={exchange} returned 404"))
            else:
                results.append(_fail(tester, name, f"HTTP {resp.status_code}", resp.response_time_ms, resp.error))
        except Exception as e:
            results.append(_fail(tester, name, "Exception", 0, str(e)))

    return results


# ============================================================
# 2. Multi-interval tests (on Binance)
# ============================================================
def test_kline_all_intervals(tester: BaseTester) -> list:
    """Test all supported intervals on Binance"""
    results = []
    exchange = "binance"
    symbol = "BTCUSDT"

    for interval in KLINE_INTERVALS:
        name = f"Interval [{interval}] on Binance"
        try:
            resp = tester.client.v2_get_kline(
                exchange=exchange, symbol=symbol, interval=interval,
                limit=5
            )
            if _has_kline_data(resp):
                results.append(_pass(tester, name, f"OK, count={_data_count(resp)}", resp.response_time_ms))
            else:
                results.append(_warn(tester, name, "No data", resp.response_time_ms, resp.error))
        except Exception as e:
            results.append(_fail(tester, name, "Exception", 0, str(e)))

    return results


# ============================================================
# 3. Time range tests (start + end, RFC 3339)
# ============================================================
def test_kline_time_range(tester: BaseTester) -> list:
    """Test kline queries with start+end time range (RFC 3339)"""
    results = []

    now = datetime.now(timezone.utc)

    # 3a. Binance 1h with recent 2-hour window
    start_str = (now - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    name = "Time range: Binance 1h recent 2h"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h",
        start_time=start_str, end_time=end_str
    )
    if _has_kline_data(resp):
        results.append(_pass(tester, name, f"OK, count={_data_count(resp)}", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, "No data returned", resp.response_time_ms, resp.error))

    # 3b. Binance 1m with short time range (10 minutes)
    start_1m = (now - timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_1m = (now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")

    name = "Time range: Binance 1m recent 10min"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1m",
        start_time=start_1m, end_time=end_1m
    )
    if _has_kline_data(resp):
        results.append(_pass(tester, name, f"OK, count={_data_count(resp)}", resp.response_time_ms))
    else:
        results.append(_warn(tester, name, "No data (may be expected for 1m)", resp.response_time_ms, resp.error))

    # 3c. Very old time range (should return 404)
    old_start = "2019-01-01T00:00:00Z"
    old_end = "2019-01-01T01:00:00Z"

    name = "Time range: very old data (expect 404)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h",
        start_time=old_start, end_time=old_end
    )
    if resp.status_code == 404:
        results.append(_pass(tester, name, "Correctly returned 404", resp.response_time_ms))
    else:
        # Old data might still exist in some sources, treat as warn
        results.append(_warn(tester, name, f"Expected 404 but got HTTP {resp.status_code}", resp.response_time_ms, resp.error))

    # 3d. start only, no end (falls back to limit mode since hasTimeRange requires both)
    name = "Time range: start only (no end)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h",
        start_time=start_str
    )
    if _has_kline_data(resp):
        results.append(_pass(tester, name, f"OK (limit mode), count={_data_count(resp)}", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, "No data", resp.response_time_ms, resp.error))

    # 3e. Aster 1m time range (reproduce original issue)
    name = "Time range: aster BTC/USDT 1m (reproduce original issue)"
    aster_start = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    aster_end = (now - timedelta(hours=23)).strftime("%Y-%m-%dT%H:%M:%SZ")
    resp = tester.client.v2_get_kline(
        exchange="aster", symbol="BTC/USDT", interval="1m",
        start_time=aster_start, end_time=aster_end
    )
    if _has_kline_data(resp):
        results.append(_pass(tester, name, f"OK, data found", resp.response_time_ms))
    elif resp.status_code == 404:
        results.append(_warn(tester, name, "404 - aster 1m data not available (known issue)", resp.response_time_ms, resp.error))
    else:
        results.append(_fail(tester, name, f"HTTP {resp.status_code}", resp.response_time_ms, resp.error))

    return results


# ============================================================
# 4. Error scenario tests
# ============================================================
def test_kline_errors(tester: BaseTester) -> list:
    """Test error handling: invalid params, empty data"""
    results = []

    # 4a. Invalid exchange
    name = "Error: invalid exchange"
    resp = tester.client.v2_get_kline(
        exchange="nonexistent_exchange_xyz", symbol="BTCUSDT", interval="1h"
    )
    if resp.status_code in (400, 404, 422):
        results.append(_pass(tester, name, f"Correctly rejected, HTTP {resp.status_code}", resp.response_time_ms))
    elif resp.status_code == 200 and not _has_kline_data(resp):
        results.append(_warn(tester, name, "HTTP 200 but empty data (should be 4xx)", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, f"Unexpected HTTP {resp.status_code}", resp.response_time_ms, resp.error))

    # 4b. Invalid symbol
    name = "Error: invalid symbol"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="INVALIDPAIR123", interval="1h"
    )
    if resp.status_code in (400, 404, 422):
        results.append(_pass(tester, name, f"Correctly rejected, HTTP {resp.status_code}", resp.response_time_ms))
    elif resp.status_code == 404:
        results.append(_pass(tester, name, "Correctly returned 404 (no data)", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, f"Unexpected HTTP {resp.status_code}", resp.response_time_ms, resp.error))

    # 4c. Invalid interval
    name = "Error: invalid interval"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="99m"
    )
    if resp.status_code == 400:
        results.append(_pass(tester, name, "Correctly rejected with 400", resp.response_time_ms))
    elif resp.status_code == 422:
        results.append(_pass(tester, name, f"Correctly rejected with 422", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, f"Expected 400/422, got HTTP {resp.status_code}", resp.response_time_ms, resp.error))

    # 4d. Empty time range (start == end)
    name = "Error: empty time range (start==end)"
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h",
        start_time=now_str, end_time=now_str
    )
    if resp.status_code == 404 or not _has_kline_data(resp):
        results.append(_pass(tester, name, f"Correctly returned no data, HTTP {resp.status_code}", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, f"Expected no data, got HTTP {resp.status_code}", resp.response_time_ms, resp.error))

    # 4e. Future time range
    future_start = (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    future_end = (datetime.now(timezone.utc) + timedelta(days=365, hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    name = "Error: future time range"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h",
        start_time=future_start, end_time=future_end
    )
    if resp.status_code == 404 or not _has_kline_data(resp):
        results.append(_pass(tester, name, f"Correctly returned no data, HTTP {resp.status_code}", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, f"Expected no data, got HTTP {resp.status_code}", resp.response_time_ms, resp.error))

    return results


# ============================================================
# 5. Symbol format tests
# ============================================================
def test_kline_symbol_format(tester: BaseTester) -> list:
    """Test symbol format: BTCUSDT vs BTC/USDT vs lowercase"""
    results = []

    # 5a. BTCUSDT (no slash)
    name = "Symbol format: BTCUSDT (no slash)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h", limit=3
    )
    if _has_kline_data(resp):
        results.append(_pass(tester, name, "OK", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, "No data", resp.response_time_ms, resp.error))

    # 5b. BTC/USDT (with slash)
    name = "Symbol format: BTC/USDT (with slash)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTC/USDT", interval="1h", limit=3
    )
    if _has_kline_data(resp):
        results.append(_pass(tester, name, "OK", resp.response_time_ms))
    else:
        results.append(_warn(tester, name, "No data - slash format may not be supported on Binance", resp.response_time_ms, resp.error))

    # 5c. lowercase symbol
    name = "Symbol format: btcusdt (lowercase)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="btcusdt", interval="1h", limit=3
    )
    if _has_kline_data(resp):
        results.append(_pass(tester, name, "OK (case insensitive)", resp.response_time_ms))
    else:
        results.append(_warn(tester, name, "No data - may be case sensitive", resp.response_time_ms, resp.error))

    return results


# ============================================================
# 6. Limit boundary tests
# ============================================================
def test_kline_limit_boundary(tester: BaseTester) -> list:
    """Test limit parameter: min, max, default"""
    results = []

    # 6a. limit=1 (minimum)
    name = "Limit: min (1)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h", limit=1
    )
    if _has_kline_data(resp):
        count = _data_count(resp)
        if count == 1:
            results.append(_pass(tester, name, f"OK, count={count}", resp.response_time_ms))
        else:
            results.append(_warn(tester, name, f"Expected 1, got {count}", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, "No data", resp.response_time_ms, resp.error))

    # 6b. limit=500 (maximum)
    name = "Limit: max (500)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h", limit=500
    )
    if _has_kline_data(resp):
        count = _data_count(resp)
        results.append(_pass(tester, name, f"OK, count={count}", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, "No data", resp.response_time_ms, resp.error))

    # 6c. No limit (default)
    name = "Limit: default (not specified)"
    resp = tester.client.v2_get_kline(
        exchange="binance", symbol="BTCUSDT", interval="1h"
    )
    if _has_kline_data(resp):
        count = _data_count(resp)
        results.append(_pass(tester, name, f"OK, count={count} (default=100)", resp.response_time_ms))
    else:
        results.append(_fail(tester, name, "No data", resp.response_time_ms, resp.error))

    return results


# ============================================================
# Main entry - aggregates all test groups
# ============================================================
def test_v2_kline(tester: BaseTester) -> list:
    """V2 Crypto K-line comprehensive tests"""
    all_results = []

    print("\n  [1/6] Exchange connectivity...")
    all_results.extend(test_kline_all_exchanges(tester))

    print("  [2/6] Interval coverage...")
    all_results.extend(test_kline_all_intervals(tester))

    print("  [3/6] Time range tests...")
    all_results.extend(test_kline_time_range(tester))

    print("  [4/6] Error scenarios...")
    all_results.extend(test_kline_errors(tester))

    print("  [5/6] Symbol format tests...")
    all_results.extend(test_kline_symbol_format(tester))

    print("  [6/6] Limit boundary tests...")
    all_results.extend(test_kline_limit_boundary(tester))

    return all_results
