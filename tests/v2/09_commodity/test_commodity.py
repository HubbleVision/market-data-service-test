"""
V2 Commodity tests
商品相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus


def test_commodity_spot(tester: BaseTester) -> list:
    """Test commodity spot price endpoint (gold/silver)"""
    results = []

    resp = tester.client.v2_av_gold_silver_spot()
    ok = resp.success
    results.append(tester._make_result(
        "Commodity: gold_silver_spot",
        "commodity_spot",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"gold_silver_spot - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_commodity_klines(tester: BaseTester) -> list:
    """Test commodity klines endpoint (gold/silver history)"""
    results = []

    resp = tester.client.v2_av_gold_silver_history(interval="daily", limit=100)
    ok = resp.success
    results.append(tester._make_result(
        "Commodity: gold_silver_history",
        "commodity_history",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"gold_silver_history - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_commodity_other(tester: BaseTester) -> list:
    """Test other commodity endpoints (WTI oil, Brent, Natural Gas)"""
    results = []

    # Test various commodity prices
    commodities = [
        ("WTI", "wti"),
        ("BRENT", "brent"),
        ("NATURAL_GAS", "natural_gas"),
    ]

    for name, label in commodities:
        try:
            resp = tester.client.v2_av_commodity(function_name=name)
            ok = resp.success
            results.append(tester._make_result(
                f"Commodity: {label}",
                f"commodity_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"Commodity: {label}",
                f"commodity_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results
