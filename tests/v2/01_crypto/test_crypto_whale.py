"""
V2 Crypto Whale tests
鲸鱼活动相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus


def test_crypto_whale(tester: BaseTester) -> list:
    """Test crypto whale activity endpoints"""
    results = []

    # Test whale positions
    resp = tester.client.v2_get_whale_positions(size="100")
    ok = resp.success
    results.append(tester._make_result(
        "CryptoWhale: positions",
        "crypto_whale_positions",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"whale_positions - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    # Test whale activity
    resp2 = tester.client.v2_get_whale_activity(size="100")
    ok2 = resp2.success
    results.append(tester._make_result(
        "CryptoWhale: activity",
        "crypto_whale_activity",
        TestStatus.PASSED if ok2 else TestStatus.FAILED,
        f"whale_activity - {'OK' if ok2 else 'FAILED'}",
        resp2.response_time_ms,
        resp2.error if not ok2 else None,
    ))

    return results
