"""
AV 扩展 — 经济指标 (新增 5 个)
覆盖: REAL_GDP_PER_CAPITA, FEDERAL_FUNDS_RATE, RETAIL_SALES,
      DURABLES, NONFARM_PAYROLL
"""
from framework import BaseTester, TestStatus


def test_av_economic_indicators(tester: BaseTester) -> list:
    """新增经济指标"""
    results = []

    indicators = [
        ("REAL_GDP_PER_CAPITA", tester.client.v2_av_real_gdp_per_capita, "人均GDP"),
        ("FEDERAL_FUNDS_RATE", tester.client.v2_av_federal_funds_rate, "联邦基金利率"),
        ("RETAIL_SALES", tester.client.v2_av_retail_sales, "零售销售"),
        ("DURABLES", tester.client.v2_av_durables, "耐用品订单"),
        ("NONFARM_PAYROLL", tester.client.v2_av_nonfarm_payroll, "非农就业"),
    ]

    for name, fn, desc in indicators:
        resp = fn()
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        if ok:
            item = items[0]
            ok = "time" in item or "date" in item

        results.append(tester._make_result(
            f"{name} ({desc})",
            "av_economic",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{desc} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
