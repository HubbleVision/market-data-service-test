"""
AV 扩展 — 外汇补全
覆盖: FX_INTRADAY, FX_WEEKLY, FX_MONTHLY
"""
from framework import BaseTester, TestStatus

FX_PAIRS = [("EUR", "USD"), ("GBP", "USD"), ("USD", "JPY")]


def test_av_fx_intraday(tester: BaseTester) -> list:
    """外汇分钟线 FX_INTRADAY"""
    results = []

    for from_ccy, to_ccy in FX_PAIRS:
        for interval in ["5min", "15min", "60min"]:
            resp = tester.client.v2_av_fx_intraday(
                from_currency=from_ccy, to_currency=to_ccy,
                interval=interval, limit=10
            )
            data = resp.data if isinstance(resp.data, dict) else {}
            ok = resp.success and data.get("success") is True

            if ok:
                items = data.get("klines") or data.get("data") or []
                ok = isinstance(items, list) and len(items) > 0

            if ok:
                item = items[0]
                ok = all(f in item for f in ["time", "open", "high", "low", "close"])

            results.append(tester._make_result(
                f"FX_INTRADAY ({from_ccy}/{to_ccy} {interval})",
                "av_fx_extended",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"外汇分钟线 - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))

    return results


def test_av_fx_weekly(tester: BaseTester) -> list:
    """外汇周线 FX_WEEKLY"""
    results = []

    for from_ccy, to_ccy in FX_PAIRS:
        resp = tester.client.v2_av_fx_weekly(
            from_currency=from_ccy, to_currency=to_ccy, limit=10
        )
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("klines") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        results.append(tester._make_result(
            f"FX_WEEKLY ({from_ccy}/{to_ccy})",
            "av_fx_extended",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"外汇周线 - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_fx_monthly(tester: BaseTester) -> list:
    """外汇月线 FX_MONTHLY"""
    results = []

    for from_ccy, to_ccy in FX_PAIRS:
        resp = tester.client.v2_av_fx_monthly(
            from_currency=from_ccy, to_currency=to_ccy, limit=10
        )
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("klines") or data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        results.append(tester._make_result(
            f"FX_MONTHLY ({from_ccy}/{to_ccy})",
            "av_fx_extended",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"外汇月线 - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
