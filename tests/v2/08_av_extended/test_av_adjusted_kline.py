"""
AV 扩展 — 复权 K 线
覆盖: TIME_SERIES_DAILY_ADJUSTED, WEEKLY_ADJUSTED, MONTHLY_ADJUSTED
"""
from framework import BaseTester, TestStatus

TEST_SYMBOLS = ["AAPL", "MSFT"]


def test_av_daily_adjusted(tester: BaseTester) -> list:
    """测试复权日 K 线"""
    results = []

    for symbol in TEST_SYMBOLS:
        resp = tester.client.v2_av_daily_adjusted(symbol=symbol, limit=10)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("klines") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            # 基础 OHLCV 字段
            required = ["time", "open", "high", "low", "close", "volume"]
            ok = all(f in item for f in required)
            # Adjusted 特有字段
            if ok:
                ok = "adjusted_close" in item or "adjClose" in item
            if ok:
                ok = "dividend_amount" in item or "dividend" in item
            if ok:
                ok = "split_coefficient" in item or "splitCoefficient" in item
            # 数值校验
            if ok:
                ok = isinstance(item.get("close"), (int, float)) and item["close"] > 0

        results.append(tester._make_result(
            f"DAILY_ADJUSTED ({symbol})",
            "av_adjusted_kline",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"复权日线 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_weekly_adjusted(tester: BaseTester) -> list:
    """测试复权周 K 线"""
    results = []

    for symbol in TEST_SYMBOLS:
        resp = tester.client.v2_av_weekly_adjusted(symbol=symbol, limit=10)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("klines") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = "adjusted_close" in item or "adjClose" in item

        results.append(tester._make_result(
            f"WEEKLY_ADJUSTED ({symbol})",
            "av_adjusted_kline",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"复权周线 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_monthly_adjusted(tester: BaseTester) -> list:
    """测试复权月 K 线"""
    results = []

    for symbol in TEST_SYMBOLS:
        resp = tester.client.v2_av_monthly_adjusted(symbol=symbol, limit=10)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("klines") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = "adjusted_close" in item or "adjClose" in item

        results.append(tester._make_result(
            f"MONTHLY_ADJUSTED ({symbol})",
            "av_adjusted_kline",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"复权月线 {symbol} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
