"""
V2 Crypto Capital Flow & Net Positions tests (3 endpoints)
"""
import time
from framework import BaseTester, TestResult, TestStatus

_END_TIME = str(int((time.time() - 24 * 3600) * 1000))


def test_capital_flow(tester: BaseTester) -> list:
    """Test all V2 capital flow and net positions endpoints"""
    results = []

    endpoints = [
        ("realtime", lambda: tester.client.v2_get_capital_flow_realtime(product_type="SWAP")),
        ("history", lambda: tester.client.v2_get_capital_flow_history(
            base_coin="BTC", product_type="SWAP", interval="1h",
            end_time=_END_TIME, size=10)),
        ("net-positions", lambda: tester.client.v2_get_net_positions(
            symbol="BTCUSDT", exchange="Binance", interval="1h",
            end_time=_END_TIME, size=10)),
    ]

    for name, fn in endpoints:
        resp = fn()
        ok = resp.success
        results.append(tester._make_result(
            f"CapitalFlow: {name}",
            "crypto_capital_flow",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"capital-flow/{name} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not ok else None,
        ))

    return results
