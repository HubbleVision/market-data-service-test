"""
AV 扩展 — 经济指标 — V2 无路由，全部 SKIP
"""
from framework import BaseTester, TestStatus


def test_av_economic_indicators(tester: BaseTester) -> list:
    """V2 无经济指标路由"""
    indicators = [
        ("REAL_GDP_PER_CAPITA", "人均GDP"),
        ("FEDERAL_FUNDS_RATE", "联邦基金利率"),
        ("RETAIL_SALES", "零售销售"),
        ("DURABLES", "耐用品订单"),
        ("NONFARM_PAYROLL", "非农就业"),
    ]
    results = []
    for name, desc in indicators:
        results.append(tester._make_result(
            f"{name} ({desc})",
            "av_economic",
            TestStatus.SKIPPED,
            f"V2 无经济指标路由",
            0,
        ))
    return results
