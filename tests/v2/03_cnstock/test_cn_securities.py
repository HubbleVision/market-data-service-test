"""
V2 CNStock securities tests: real-time quote from Fosun
"""
from framework import BaseTester, TestResult, TestStatus

CN_SECURITIES_CODES = "600519,000001"


def test_cnstock_securities(tester: BaseTester) -> list:
    """Test V2 cnstock securities endpoint"""
    results = []

    # 1. Basic: multi-code query
    resp = tester.client.v2_get_cnstock_securities(codes=CN_SECURITIES_CODES)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = data.get("success") is True
    if ok:
        quote_data = data.get("data")
        ok = isinstance(quote_data, dict) and len(quote_data) > 0
    if ok:
        for code in CN_SECURITIES_CODES.split(","):
            code = code.strip()
            if code not in quote_data:
                ok = False
                break

    results.append(tester._make_result(
        "CNStock: securities (multi-code)",
        "cnstock_securities_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"securities({CN_SECURITIES_CODES}) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. Fields filter
    resp2 = tester.client.v2_get_cnstock_securities(codes="600519", fields="name,price,chgPct")
    ok2 = resp2.success
    data2 = resp2.data if isinstance(resp2.data, dict) else {}
    if ok2:
        ok2 = data2.get("success") is True
    if ok2:
        quote_data2 = data2.get("data", {})
        ok2 = isinstance(quote_data2, dict) and "600519" in quote_data2
    if ok2:
        item = quote_data2["600519"]
        ok2 = "name" in item and "price" in item and "chgPct" in item

    results.append(tester._make_result(
        "CNStock: securities (fields filter)",
        "cnstock_securities_fields",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"securities(600519, fields=name,price,chgPct) - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    # 3. Response structure: timestamp exists
    resp3 = tester.client.v2_get_cnstock_securities(codes="600519")
    ok3 = resp3.success
    data3 = resp3.data if isinstance(resp3.data, dict) else {}
    if ok3:
        ok3 = data3.get("success") is True and isinstance(data3.get("timestamp"), int)

    results.append(tester._make_result(
        "CNStock: securities (response structure)",
        "cnstock_securities_structure",
        TestStatus.PASSED if ok3 else TestStatus.FAILED,
        f"securities structure check - {'OK' if ok3 else 'FAILED'}",
        resp3.response_time_ms,
        resp3.error if not ok3 else None,
    ))

    return results
