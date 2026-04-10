"""
AV 扩展 — 加密货币周/月线
覆盖: DIGITAL_CURRENCY_WEEKLY, DIGITAL_CURRENCY_MONTHLY
"""
from framework import BaseTester, TestStatus

CRYPTO_PAIRS = [("BTC", "USD"), ("ETH", "USD")]


def test_av_crypto_weekly(tester: BaseTester) -> list:
    """加密货币周线"""
    results = []

    for symbol, market in CRYPTO_PAIRS:
        resp = tester.client.v2_av_crypto_weekly(symbol=symbol, market=market, limit=10)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("klines") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = all(f in item for f in ["time", "open", "high", "low", "close"])

        results.append(tester._make_result(
            f"DIGITAL_CURRENCY_WEEKLY ({symbol}/{market})",
            "av_crypto_extended",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"加密周线 - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_crypto_monthly(tester: BaseTester) -> list:
    """加密货币月线"""
    results = []

    for symbol, market in CRYPTO_PAIRS:
        resp = tester.client.v2_av_crypto_monthly(symbol=symbol, market=market, limit=10)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("klines") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = all(f in item for f in ["time", "open", "high", "low", "close"])

        results.append(tester._make_result(
            f"DIGITAL_CURRENCY_MONTHLY ({symbol}/{market})",
            "av_crypto_extended",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"加密月线 - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
