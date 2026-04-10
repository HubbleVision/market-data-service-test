"""
Service health check tests
"""
from framework import BaseTester, TestResult, TestStatus


def test_health(tester: BaseTester) -> list:
    """Test service health endpoint"""
    results = []

    resp = tester.client.health_check()
    ok = resp.success
    results.append(tester._make_result(
        "Health Check",
        "common",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"/api/v1/health - {'OK' if ok else resp.error}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
