"""
V2 Crypto Indicators tests
加密货币特色指标测试
"""
from framework import BaseTester, TestResult, TestStatus

# Crypto indicator endpoints - no parameters required
CRYPTO_INDICATORS = [
    ("fear_greed", "v2_get_crypto_indicator_fear_greed"),
    ("ahr999", "v2_get_crypto_indicator_ahr999"),
    ("two_year_ma", "v2_get_crypto_indicator_two_year_ma"),
    ("btc_dominance", "v2_get_crypto_indicator_btc_dominance"),
    ("puell", "v2_get_crypto_indicator_puell"),
    ("pi_cycle", "v2_get_crypto_indicator_pi_cycle"),
    ("altcoin_index", "v2_get_crypto_indicator_altcoin_index"),
    ("grayscale", "v2_get_crypto_indicator_grayscale"),
]


def test_crypto_indicators(tester: BaseTester) -> list:
    """Test V2 crypto indicator endpoints"""
    results = []

    for label, method_name in CRYPTO_INDICATORS:
        method = getattr(tester.client, method_name, None)
        if method is None:
            results.append(tester._make_result(
                f"CryptoIndicator: {label}",
                f"crypto_indicator_{label}",
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
                f"CryptoIndicator: {label}",
                f"crypto_indicator_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"CryptoIndicator: {label}",
                f"crypto_indicator_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results
