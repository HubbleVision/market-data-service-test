# V1 LEGACY - to be removed when V2 migration is complete
from framework import BaseTester, TestResult, TestStatus


def test_reference(tester: BaseTester) -> list:
    results = []
    ts_code = "000001.SZ"

    # 1. get_holders_top10
    resp = tester.client.get_holders_top10(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: holders top10",
        "v1_holders_top10",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"holders_top10 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. get_holders_float_top10
    resp = tester.client.get_holders_float_top10(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: holders float_top10",
        "v1_holders_float_top10",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"holders_float_top10 - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 3. get_holders_number
    resp = tester.client.get_holders_number(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: holders number",
        "v1_holders_number",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"holders_number - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 4. get_repurchase
    resp = tester.client.get_repurchase(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: repurchase",
        "v1_repurchase",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"repurchase - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 5. get_block_trade
    resp = tester.client.get_block_trade(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: block_trade",
        "v1_block_trade",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"block_trade - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 6. get_share_float
    resp = tester.client.get_share_float(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: share_float",
        "v1_share_float",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"share_float - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 7. get_pledge
    resp = tester.client.get_pledge(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: pledge",
        "v1_pledge",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"pledge - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 8. get_pledge_stat
    resp = tester.client.get_pledge_stat(ts_code=ts_code, limit=5)
    ok = resp.success
    results.append(tester._make_result(
        "V1: pledge_stat",
        "v1_pledge_stat",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"pledge_stat - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
