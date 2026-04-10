"""
V2 CNStock holders and reference tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_cnstock_holders(tester: BaseTester) -> list:
    """Test V2 cnstock holders and reference endpoints"""
    results = []
    ts_code = "000001.SZ"

    # 1. v2_get_holders_top10
    resp = tester.client.v2_get_holders_top10(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: holders top10",
        "cnstock_holders_top10",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"holders top10 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. v2_get_holders_float_top10
    resp = tester.client.v2_get_holders_float_top10(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: holders float top10",
        "cnstock_holders_float_top10",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"holders float top10 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. v2_get_holders_number
    resp = tester.client.v2_get_holders_number(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: holders number",
        "cnstock_holders_number",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"holders number - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. v2_get_repurchase
    resp = tester.client.v2_get_repurchase(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: repurchase",
        "cnstock_repurchase",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"repurchase - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. v2_get_block_trade
    resp = tester.client.v2_get_block_trade(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: block trade",
        "cnstock_block_trade",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"block trade - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. v2_get_share_float
    resp = tester.client.v2_get_share_float(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: share float",
        "cnstock_share_float",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"share float - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 7. v2_get_pledge
    resp = tester.client.v2_get_pledge(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: pledge",
        "cnstock_pledge",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"pledge - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 8. v2_get_pledge_stat
    resp = tester.client.v2_get_pledge_stat(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "CNStock: pledge stat",
        "cnstock_pledge_stat",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"pledge stat - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
