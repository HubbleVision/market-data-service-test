"""
AV 扩展 — 外汇 — V2 无 FX 路由，全部 SKIP
V2 /api/v2/index/klines 仅支持指数代码 (SPX, DJI 等)，不支持货币对 (EUR/USD)
"""
from framework import BaseTester, TestStatus


def test_av_fx_intraday(tester: BaseTester) -> list:
    """V2 无 FX 路由"""
    return [tester._make_result(
        "FX_INTRADAY",
        "av_fx_extended",
        TestStatus.SKIPPED,
        "V2 无外汇路由 (index/klines 仅支持指数代码)",
        0,
    )]


def test_av_fx_weekly(tester: BaseTester) -> list:
    """V2 无 FX 路由"""
    return [tester._make_result(
        "FX_WEEKLY",
        "av_fx_extended",
        TestStatus.SKIPPED,
        "V2 无外汇路由 (index/klines 仅支持指数代码)",
        0,
    )]


def test_av_fx_monthly(tester: BaseTester) -> list:
    """V2 无 FX 路由"""
    return [tester._make_result(
        "FX_MONTHLY",
        "av_fx_extended",
        TestStatus.SKIPPED,
        "V2 无外汇路由 (index/klines 仅支持指数代码)",
        0,
    )]
