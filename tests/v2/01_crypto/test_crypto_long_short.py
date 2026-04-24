"""
V2 Crypto Long/Short tests
多空比相关接口测试
"""
from framework import BaseTester, TestResult, TestStatus

TEST_EXCHANGE = "binance"
TEST_SYMBOL = "BTC-USDT"
TEST_BASE_COIN = "BTC"
TEST_INTERVAL = "1h"


def test_crypto_long_short_exchange(tester: BaseTester) -> list:
    """Test long/short exchange ratio endpoint"""
    results = []

    resp = tester.client.v2_get_long_short_exchange(
        base_coin=TEST_BASE_COIN,
        interval=TEST_INTERVAL,
        size=100
    )
    ok = resp.success
    results.append(tester._make_result(
        "CryptoLS: exchange",
        "crypto_ls_exchange",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"ls_exchange - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_crypto_long_short_account(tester: BaseTester) -> list:
    """Test long/short account endpoints"""
    results = []

    endpoints = [
        ("ls_account", lambda: tester.client.v2_get_long_short_account(
            symbol=TEST_SYMBOL, exchange=TEST_EXCHANGE, interval=TEST_INTERVAL, size=100)),
        ("ls_top_trader", lambda: tester.client.v2_get_long_short_top_trader(
            symbol=TEST_SYMBOL, exchange=TEST_EXCHANGE, interval=TEST_INTERVAL, size=100)),
        ("ls_top_trader_account", lambda: tester.client.v2_get_long_short_top_trader_account(
            symbol=TEST_SYMBOL, exchange=TEST_EXCHANGE, interval=TEST_INTERVAL, size=100)),
    ]

    for label, method in endpoints:
        try:
            resp = method()
            ok = resp.success
            results.append(tester._make_result(
                f"CryptoLS: {label}",
                f"crypto_{label}",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"{label} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not ok else None,
            ))
        except Exception as e:
            results.append(tester._make_result(
                f"CryptoLS: {label}",
                f"crypto_{label}",
                TestStatus.FAILED,
                f"{label} - EXCEPTION",
                0,
                str(e),
            ))

    return results


def test_crypto_long_short_kline(tester: BaseTester) -> list:
    """Test long/short kline endpoint"""
    results = []

    resp = tester.client.v2_get_long_short_kline(
        type_="account",
        symbol=TEST_SYMBOL,
        exchange=TEST_EXCHANGE,
        interval=TEST_INTERVAL,
        size=100
    )
    ok = resp.success
    results.append(tester._make_result(
        "CryptoLS: kline",
        "crypto_ls_kline",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"ls_kline - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results


def test_crypto_long_short_taker(tester: BaseTester) -> list:
    """Test long/short taker ratio endpoint"""
    results = []

    resp = tester.client.v2_get_long_short_taker_ratio(
        base_coin=TEST_BASE_COIN,
        interval=TEST_INTERVAL,
        size=100
    )
    ok = resp.success
    results.append(tester._make_result(
        "CryptoLS: taker_ratio",
        "crypto_ls_taker_ratio",
        TestStatus.PASSED if ok else TestStatus.FAILED,
        f"ls_taker_ratio - {'OK' if ok else 'FAILED'}",
        resp.response_time_ms,
        resp.error if not ok else None,
    ))

    return results
