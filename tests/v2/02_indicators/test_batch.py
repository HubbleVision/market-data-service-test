"""
V2 batch indicator POST endpoint tests
Tests POST /api/v2/indicators/batch with multiple indicators across markets
"""
from framework import BaseTester, TestResult, TestStatus
from config import V2_MARKET_CONFIG


def test_batch_indicators(tester: BaseTester) -> list:
    """Test V2 batch indicator POST endpoint (crypto and cn)"""
    results = []

    batch_items = {
        "crypto": [
            {"type": "sma", "params": [20]},
            {"type": "rsi", "params": [14]},
            {"type": "macd", "params": [12, 26, 9]},
        ],
        "cn": [
            {"type": "sma", "params": [20]},
            {"type": "rsi", "params": [14]},
        ],
    }

    for market in ("crypto", "cn"):
        cfg = V2_MARKET_CONFIG[market]
        resp = tester.client.post_v2_indicators_batch(
            market=market,
            symbol=cfg["symbol"],
            exchange=cfg.get("exchange") or None,
            interval=cfg["interval"],
            indicators=batch_items.get(market, []),
        )

        data = resp.data if isinstance(resp.data, dict) else {}
        ok = resp.success

        if ok:
            if "times" not in data or not data.get("indicators"):
                ok = False
            if data.get("market") != market:
                ok = False

        results.append(tester._make_result(
            f"Batch: {market}",
            "batch_v2",
            TestStatus.PASSED if ok else TestStatus.FAILED,
            f"batch POST {market} - {'OK' if ok else 'FAILED'}",
            resp.response_time_ms,
            resp.error if not resp.success else None,
        ))

    return results
