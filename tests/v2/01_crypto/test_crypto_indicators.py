"""
V2 Crypto On-chain Indicator tests (8 endpoints)
Fear & Greed, AHR999, BTC Dominance, Puell, Pi Cycle, 2-Year MA, Altcoin Index, Grayscale
"""
from framework import BaseTester, TestResult, TestStatus


def test_crypto_indicators(tester: BaseTester) -> list:
    """Test all V2 crypto on-chain indicator endpoints"""
    results = []

    endpoints = [
        ("fear-greed", lambda: tester.client.v2_get_crypto_indicator_fear_greed()),
        ("ahr999", lambda: tester.client.v2_get_crypto_indicator_ahr999()),
        ("btc-dominance", lambda: tester.client.v2_get_crypto_indicator_btc_dominance()),
        ("puell", lambda: tester.client.v2_get_crypto_indicator_puell()),
        ("pi-cycle", lambda: tester.client.v2_get_crypto_indicator_pi_cycle()),
        ("two-year-ma", lambda: tester.client.v2_get_crypto_indicator_two_year_ma()),
        ("altcoin-index", lambda: tester.client.v2_get_crypto_indicator_altcoin_index()),
        ("grayscale", lambda: tester.client.v2_get_crypto_indicator_grayscale()),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"CryptoIndicator: {name}",
            "crypto_indicator",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"indicator/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
