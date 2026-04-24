"""
V2 Crypto Ranking tests
加密货币排行相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus

RANKING_ENDPOINTS = [
    ("open_interest", "v2_get_ranking_open_interest"),
    ("volume", "v2_get_ranking_volume"),
    ("price_change", "v2_get_ranking_price_change"),
    ("liquidation", "v2_get_ranking_liquidation"),
]


def test_crypto_ranking(tester: BaseTester) -> list:
    """Test V2 crypto ranking endpoints"""
    results = []

    for label, method_name in RANKING_ENDPOINTS:
        method = getattr(tester.client, method_name, None)
        if method is None:
            results.append(tester._make_result(
                f"CryptoRanking: {label}",
                f"crypto_ranking_{label}",
                TestStatus.FAILED,
                f"{label}: method {method_name} not found",
                0,
                f"Method {method_name} does not exist on client",
            ))
            continue

        try:
            resp = method()
            ok = resp.success
            results.append(tester._make_result(
                f"CryptoRanking: {label}",
                f"crypto_ranking_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"CryptoRanking: {label}",
                f"crypto_ranking_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results
