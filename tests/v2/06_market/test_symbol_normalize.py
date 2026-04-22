"""
Symbol 标准化测试 — V2 版本
V1 统一接口 (/api/v1/stock/klines) 已下线，V2 无等价路由。
本测试已废弃，全部返回 SKIPPED。
"""
from framework import BaseTester, TestStatus


def test_symbol_normalize(tester: BaseTester) -> list:
    """V1 统一股票接口已下线，无 V2 替代"""
    return [tester._make_result(
        "Symbol标准化: V1已下线",
        "symbol_normalize",
        TestStatus.SKIPPED,
        "V1 unified stock endpoint deprecated, no V2 equivalent",
        0,
    )]
