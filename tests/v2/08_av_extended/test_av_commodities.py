"""
AV 扩展 — 商品专用端点 (P1)
覆盖: GOLD_SILVER_SPOT, GOLD_SILVER_HISTORY, NATURAL_GAS, COPPER,
      ALUMINUM, WHEAT, CORN, COTTON, SUGAR, COFFEE, ALL_COMMODITIES
"""
from framework import BaseTester, TestStatus

COMMODITIES = [
    ("NATURAL_GAS", "天然气"),
    ("COPPER", "铜"),
    ("ALUMINUM", "铝"),
    ("WHEAT", "小麦"),
    ("CORN", "玉米"),
    ("COTTON", "棉花"),
    ("SUGAR", "糖"),
    ("COFFEE", "咖啡"),
]


def test_av_gold_silver_spot(tester: BaseTester) -> list:
    """贵金属现货 GOLD_SILVER_SPOT"""
    results = []
    resp = tester.client.v2_av_gold_silver_spot()
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    if ok:
        ok = isinstance(data.get("data"), dict) or isinstance(data.get("data"), list)

    results.append(tester._make_result(
        "GOLD_SILVER_SPOT",
        "av_commodities",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"贵金属现货 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results


def test_av_gold_silver_history(tester: BaseTester) -> list:
    """贵金属历史 GOLD_SILVER_HISTORY"""
    results = []

    for interval in ["daily", "weekly", "monthly"]:
        resp = tester.client.v2_av_gold_silver_history(interval=interval, limit=10)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        if ok:
            items = data.get("data") or []
            ok = isinstance(items, list) and len(items) > 0

        results.append(tester._make_result(
            f"GOLD_SILVER_HISTORY (interval={interval})",
            "av_commodities",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"贵金属历史 - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_commodity_individual(tester: BaseTester) -> list:
    """各商品品种"""
    results = []

    for func_name, desc in COMMODITIES:
        resp = tester.client.v2_av_commodity(function_name=func_name)
        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success and data.get("success") is True

        results.append(tester._make_result(
            f"COMMODITY ({func_name} - {desc})",
            "av_commodities",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"{desc} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results


def test_av_all_commodities(tester: BaseTester) -> list:
    """大宗商品指数 ALL_COMMODITIES"""
    results = []
    resp = tester.client.v2_av_commodity(function_name="ALL_COMMODITIES")
    data = resp.data if isinstance(resp.data, dict) else {}
    ok = resp.success and data.get("success") is True

    results.append(tester._make_result(
        "ALL_COMMODITIES",
        "av_commodities",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"商品指数 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))
    return results
