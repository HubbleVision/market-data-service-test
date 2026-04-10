"""
V2 HKStock securities tests: real-time quote from Fosun
"""
from framework import BaseTester, TestResult, TestStatus

HK_SECURITIES_CODES = "00700,00941"


def test_hkstock_securities(tester: BaseTester) -> list:
    """Test V2 hkstock securities endpoint"""
    results = []

    # 1. Basic: multi-code query
    resp = tester.client.v2_get_hkstock_securities(codes=HK_SECURITIES_CODES)
    ok = resp.success
    data = resp.data if isinstance(resp.data, dict) else {}
    if ok:
        ok = data.get("success") is True
    if ok:
        quote_data = data.get("data")
        ok = isinstance(quote_data, dict) and len(quote_data) > 0
    if ok:
        # verify each requested code exists
        for code in HK_SECURITIES_CODES.split(","):
            code = code.strip()
            if code not in quote_data:
                ok = False
                break

    results.append(tester._make_result(
        "HKStock: securities (multi-code)",
        "hkstock_securities_basic",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"securities({HK_SECURITIES_CODES}) - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # 2. Fields filter
    resp2 = tester.client.v2_get_hkstock_securities(codes="00700", fields="name,price,chgPct")
    ok2 = resp2.success
    data2 = resp2.data if isinstance(resp2.data, dict) else {}
    if ok2:
        ok2 = data2.get("success") is True
    if ok2:
        quote_data2 = data2.get("data", {})
        ok2 = isinstance(quote_data2, dict) and "00700" in quote_data2
    if ok2:
        item = quote_data2["00700"]
        ok2 = "name" in item and "price" in item and "chgPct" in item

    results.append(tester._make_result(
        "HKStock: securities (fields filter)",
        "hkstock_securities_fields",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"securities(00700, fields=name,price,chgPct) - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    # 3. Response structure: timestamp exists
    resp3 = tester.client.v2_get_hkstock_securities(codes="00700")
    ok3 = resp3.success
    data3 = resp3.data if isinstance(resp3.data, dict) else {}
    if ok3:
        ok3 = data3.get("success") is True and isinstance(data3.get("timestamp"), int)

    results.append(tester._make_result(
        "HKStock: securities (response structure)",
        "hkstock_securities_structure",
        TestStatus.PASSED if ok3 else TestStatus.FAILED,
        f"securities structure check - {'OK' if ok3 else 'FAILED'}",
        resp3.response_time_ms,
        resp3.error if not ok3 else None,
    ))

    # 4. Single code query with full data validation
    resp4 = tester.client.v2_get_hkstock_securities(codes="00700")
    ok4 = resp4.success
    data4 = resp4.data if isinstance(resp4.data, dict) else {}
    if ok4:
        quote_data4 = data4.get("data", {})
        ok4 = isinstance(quote_data4, dict) and "00700" in quote_data4
    if ok4:
        item = quote_data4["00700"]
        ok4 = isinstance(item.get("price"), (int, float)) and item["price"] > 0
    if ok4:
        ok4 = isinstance(item.get("name"), str) and len(item["name"]) > 0
    if ok4:
        ok4 = isinstance(item.get("chgPct"), (int, float))

    results.append(tester._make_result(
        "HKStock: securities (single code data validation)",
        "hkstock_securities_single_data",
        TestStatus.PASSED if ok4 else TestStatus.FAILED,
        f"securities(00700) data fields check - {'OK' if ok4 else 'FAILED'}",
        resp4.response_time_ms,
        resp4.error if not ok4 else None,
    ))

    # 5. Batch query (multiple codes)
    batch_codes = "00700,00941,00005,09988,01810"
    resp5 = tester.client.v2_get_hkstock_securities(codes=batch_codes)
    ok5 = resp5.success
    data5 = resp5.data if isinstance(resp5.data, dict) else {}
    if ok5:
        ok5 = data5.get("success") is True
    if ok5:
        quote_data5 = data5.get("data")
        ok5 = isinstance(quote_data5, dict) and len(quote_data5) >= 3

    results.append(tester._make_result(
        "HKStock: securities (batch query)",
        "hkstock_securities_batch",
        TestStatus.PASSED if ok5 else TestStatus.FAILED,
        f"securities({batch_codes}) batch check - {'OK' if ok5 else 'FAILED'}",
        resp5.response_time_ms,
        resp5.error if not ok5 else None,
    ))

    # 6. Invalid code handling
    resp6 = tester.client.v2_get_hkstock_securities(codes="99999")
    ok6 = resp6.success
    data6 = resp6.data if isinstance(resp6.data, dict) else {}
    if ok6:
        # invalid code should either return success with empty data for that code,
        # or still return a valid response structure
        ok6 = data6.get("success") is True and isinstance(data6.get("data"), dict)

    results.append(tester._make_result(
        "HKStock: securities (invalid code)",
        "hkstock_securities_invalid",
        TestStatus.PASSED if ok6 else TestStatus.FAILED,
        f"securities(99999) error handling - {'OK' if ok6 else 'FAILED'}",
        resp6.response_time_ms,
        resp6.error if not ok6 else None,
    ))

    # 7. Common fields existence check (full fields response)
    resp7 = tester.client.v2_get_hkstock_securities(codes="00700")
    ok7 = resp7.success
    data7 = resp7.data if isinstance(resp7.data, dict) else {}
    if ok7:
        item = data7.get("data", {}).get("00700", {})
        required_fields = ["price", "open", "high", "low", "volume"]
        ok7 = all(f in item for f in required_fields)

    results.append(tester._make_result(
        "HKStock: securities (common fields check)",
        "hkstock_securities_fields_exist",
        TestStatus.PASSED if ok7 else TestStatus.FAILED,
        f"securities(00700) common fields (open/high/low/volume) - {'OK' if ok7 else 'FAILED'}",
        resp7.response_time_ms,
        resp7.error if not ok7 else None,
    ))

    return results
