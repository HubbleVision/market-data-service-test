"""
V2 Technical Indicator API Tests
Tests all 27 single-indicator GET endpoints across crypto/cn markets,
validates HK/US return 501, and tests the batch POST endpoint.
"""
from typing import List, Dict, Set
from test_base import BaseTester, TestResult, TestStatus
from config import V2_INDICATORS, V2_INDICATOR_PARAMS, V2_MARKET_CONFIG

# 多值指标的响应中不含统一的 "values" 字段，而是有各自命名的数组字段
MULTI_VALUE_INDICATORS: Dict[str, List[str]] = {
    "macd":   ["dif", "dea", "macd"],
    "boll":   ["upper", "middle", "lower"],
    "kdj":    ["k", "d", "j"],
    "adx":    ["adx", "pdi", "mdi"],
    "aroon":  ["up", "down", "oscillator"],
    "ppo":    ["values", "signal", "histogram"],
    "stoch":  ["k", "d"],
    "adosc":  ["values", "fast_period", "slow_period"],
}


class V2IndicatorTester(BaseTester):
    """Test V2 technical indicator endpoints"""

    def __init__(self, base_url: str = None):
        super().__init__(base_url)
        self.indicators: List[str] = V2_INDICATORS
        self.indicator_params: Dict = V2_INDICATOR_PARAMS
        self.markets: Dict = V2_MARKET_CONFIG

    # ----------------------------------------------------------------
    # 1. 参数校验测试
    # ----------------------------------------------------------------

    def test_validation(self) -> List[TestResult]:
        """验证 market 必填、枚举校验、crypto 需要 exchange 等规则"""
        results = []

        # 1a. 不传 market → 422 (Huma required param)
        resp = self.client.get("/api/v2/indicators/sma", params={
            "symbol": "000001.SZ", "interval": "1d"
        })
        results.append(self._make_result(
            "Validation: missing market",
            "validation",
            TestStatus.PASSED if resp.status_code == 422 else TestStatus.FAILED,
            f"Expected 422, got {resp.status_code}",
            resp.response_time_ms,
            resp.error,
        ))

        # 1b. 非法 market → 422 (Huma enum 校验返回 422)
        resp = self.client.get("/api/v2/indicators/sma", params={
            "market": "invalid", "symbol": "000001.SZ", "interval": "1d"
        })
        results.append(self._make_result(
            "Validation: invalid market value",
            "validation",
            TestStatus.PASSED if resp.status_code == 422 else TestStatus.FAILED,
            f"Expected 422, got {resp.status_code}",
            resp.response_time_ms,
            resp.error,
        ))

        # 1c. crypto 不传 exchange → 400
        resp = self.client.get("/api/v2/indicators/sma", params={
            "market": "crypto", "symbol": "BTCUSDT", "interval": "1d"
        })
        results.append(self._make_result(
            "Validation: crypto without exchange",
            "validation",
            TestStatus.PASSED if resp.status_code == 400 else TestStatus.FAILED,
            f"Expected 400, got {resp.status_code}",
            resp.response_time_ms,
            resp.error,
        ))

        # 1d. crypto + cn 正常请求 → 200
        for market in ("crypto", "cn"):
            cfg = self.markets[market]
            params = {
                "market": market,
                "symbol": cfg["symbol"],
                "interval": cfg["interval"],
            }
            if cfg.get("exchange"):
                params["exchange"] = cfg["exchange"]
            resp = self.client.get("/api/v2/indicators/sma", params=params)
            results.append(self._make_result(
                f"Validation: {market} normal request",
                "validation",
                TestStatus.PASSED if resp.status_code == 200 else TestStatus.FAILED,
                f"market={market}, Expected 200, got {resp.status_code}",
                resp.response_time_ms,
                resp.error,
            ))

        return results

    # ----------------------------------------------------------------
    # 2. 指标 × 市场 功能测试
    # ----------------------------------------------------------------

    def test_all_indicators_all_markets(self) -> List[TestResult]:
        """测试每个指标在 crypto 和 cn 市场上的正常响应，hk/us 期望 501"""
        results = []

        for market, cfg in self.markets.items():
            self._log(f"\n--- Testing all indicators for market: {market} ---")
            is_stub = market in ("hk", "us")

            for indicator in self.indicators:
                params = {
                    "market": market,
                    "symbol": cfg["symbol"],
                    "interval": cfg["interval"],
                }
                if cfg.get("exchange"):
                    params["exchange"] = cfg["exchange"]
                params.update(self.indicator_params.get(indicator, {}))

                resp = self.client.get(f"/api/v2/indicators/{indicator}", params=params)

                if is_stub:
                    # 桩实现统一期望 501
                    ok = resp.status_code == 501
                    message = f"{market}/{indicator}" if ok else (
                        f"{market}/{indicator}: expected 501, got {resp.status_code}"
                    )
                    results.append(self._make_result(
                        f"Indicator: {market}/{indicator}",
                        "indicator_v2",
                        TestStatus.PASSED if ok else TestStatus.FAILED,
                        message,
                        resp.response_time_ms,
                        resp.error if not ok else None,
                    ))
                    continue

                # crypto / cn：期望 200
                data = resp.data if isinstance(resp.data, dict) else {}
                ok = resp.success
                msg_parts: List[str] = []

                if ok:
                    if not self._validate_response_structure(indicator, data, market, msg_parts):
                        ok = False

                message = f"{market}/{indicator}" if ok else f"{market}/{indicator}: {', '.join(msg_parts)}"

                results.append(self._make_result(
                    f"Indicator: {market}/{indicator}",
                    "indicator_v2",
                    TestStatus.PASSED if ok else TestStatus.FAILED,
                    message,
                    resp.response_time_ms,
                    resp.error if not resp.success else None,
                ))

        return results

    def _validate_response_structure(self, indicator: str, data: dict,
                                     market: str, msg_parts: List[str]) -> bool:
        """校验响应结构，返回 True 表示通过"""
        ok = True

        # 通用字段
        if "times" not in data:
            ok = False
            msg_parts.append("missing times")
        if data.get("market") != market:
            ok = False
            msg_parts.append(f"market mismatch: {data.get('market')}")
        if not isinstance(data.get("count"), int) or data.get("count", 0) <= 0:
            ok = False
            msg_parts.append(f"count={data.get('count')}")

        # 按指标类型校验值字段
        if indicator in MULTI_VALUE_INDICATORS:
            expected_fields = MULTI_VALUE_INDICATORS[indicator]
            for field in expected_fields:
                if field not in data:
                    ok = False
                    msg_parts.append(f"missing {field}")
        else:
            # 单值指标
            if "values" not in data:
                ok = False
                msg_parts.append("missing values")

        return ok

    # ----------------------------------------------------------------
    # 3. 指标计算值合理性校验
    # ----------------------------------------------------------------

    def test_indicator_value_sanity(self) -> List[TestResult]:
        """验证指标计算值在合理范围内（仅 crypto 市场）"""
        results = []
        cfg = self.markets["crypto"]

        sanity_rules = {
            "sma":  self._check_positive_or_zero,
            "ema":  self._check_positive_or_zero,
            "rsi":  self._check_range(0, 100),
            "macd": self._check_macd,
            "boll": self._check_boll,
            "kdj":  self._check_kdj,
            "atr":  self._check_positive,
            "natr": self._check_range(0, 100),
            "cci":  self._check_no_restrict,     # CCI 可能为负
            "adx":  self._check_range(0, 100),
            "vwap": self._check_positive,
            "obv":  self._check_no_restrict,     # OBV 可能为负
            "stddev": self._check_positive,
            "mfi":  self._check_range(0, 100),
            "willr": self._check_range(-100, 0),
            "aroon": self._check_aroon,
            "sar":  self._check_positive,
            "trix": self._check_no_restrict,     # TRIX 可能为负
            "mom":  self._check_no_restrict,
            "roc":  self._check_no_restrict,
            "cmo":  self._check_range(-100, 100),
            "ultosc": self._check_range(0, 100),
            "ppo":  self._check_ppo,
            "stoch": self._check_range(0, 100),
            "ad":   self._check_no_restrict,
            "adosc": self._check_no_restrict,
            "ht_trendline": self._check_no_restrict,
        }

        for indicator, check_fn in sanity_rules.items():
            params = {
                "market": "crypto",
                "symbol": cfg["symbol"],
                "exchange": cfg["exchange"],
                "interval": cfg["interval"],
            }
            params.update(self.indicator_params.get(indicator, {}))

            resp = self.client.get(f"/api/v2/indicators/{indicator}", params=params)
            data = resp.data if isinstance(resp.data, dict) else {}

            if not resp.success:
                results.append(self._make_result(
                    f"Sanity: crypto/{indicator}",
                    "sanity",
                    TestStatus.SKIPPED,
                    f"skipped: request failed ({resp.status_code})",
                    resp.response_time_ms,
                    resp.error,
                ))
                continue

            passed, reason = check_fn(indicator, data)
            status = TestStatus.PASSED if passed else TestStatus.FAILED
            message = f"crypto/{indicator}" if passed else f"crypto/{indicator}: {reason}"

            results.append(self._make_result(
                f"Sanity: crypto/{indicator}",
                "sanity",
                status,
                message,
                resp.response_time_ms,
                None,
            ))

        return results

    # --- sanity check helpers ---

    def _all_values(self, indicator: str, data: dict) -> List[float]:
        """从响应中提取所有指标值（兼容单值和多值指标）"""
        if indicator in MULTI_VALUE_INDICATORS:
            fields = MULTI_VALUE_INDICATORS[indicator]
            vals = []
            for f in fields:
                v = data.get(f)
                if isinstance(v, list):
                    vals.extend(v)
            return vals
        return data.get("values", [])

    def _check_positive(self, indicator, data):
        vals = self._all_values(indicator, data)
        negatives = [v for v in vals if v < 0]
        if negatives:
            return False, f"found {len(negatives)} negative values (min={min(negatives):.4f})"
        return True, ""

    def _check_positive_or_zero(self, indicator, data):
        vals = self._all_values(indicator, data)
        negatives = [v for v in vals if v < 0]
        if negatives:
            return False, f"found {len(negatives)} negative values (min={min(negatives):.4f})"
        return True, ""

    def _check_range(self, lo, hi):
        def checker(indicator, data):
            vals = self._all_values(indicator, data)
            # 跳过 NaN / 0 用于预热期
            valid = [v for v in vals if v != 0]
            if not valid:
                return True, ""  # 全部为预热占位，跳过
            out_of_range = [v for v in valid if v < lo or v > hi]
            if out_of_range:
                return False, f"{len(out_of_range)} values out of [{lo},{hi}] (min={min(out_of_range):.4f}, max={max(out_of_range):.4f})"
            return True, ""
        return checker

    def _check_no_restrict(self, indicator, data):
        vals = self._all_values(indicator, data)
        if not vals:
            return False, "no values returned"
        return True, ""

    def _check_macd(self, indicator, data):
        dif = data.get("dif", [])
        dea = data.get("dea", [])
        macd_hist = data.get("macd", [])
        if not dif or not dea or not macd_hist:
            return False, "missing dif/dea/macd fields"
        if len(dif) != len(dea) or len(dif) != len(macd_hist):
            return False, f"length mismatch: dif={len(dif)}, dea={len(dea)}, macd={len(macd_hist)}"
        # MACD histogram ≈ DIF - DEA（可能存在浮点误差）
        for i in range(len(dif)):
            expected = dif[i] - dea[i]
            diff = abs(macd_hist[i] - expected)
            if diff > abs(expected) * 0.01 + 1e-8:
                return False, f"macd[{i}]={macd_hist[i]:.6f} != dif-dea={expected:.6f}"
        return True, ""

    def _check_boll(self, indicator, data):
        upper = data.get("upper", [])
        middle = data.get("middle", [])
        lower = data.get("lower", [])
        if not upper or not middle or not lower:
            return False, "missing upper/middle/lower fields"
        for i in range(len(upper)):
            if upper[i] < middle[i]:
                return False, f"upper[{i}]={upper[i]:.4f} < middle[{i}]={middle[i]:.4f}"
            if middle[i] < lower[i]:
                return False, f"middle[{i}]={middle[i]:.4f} < lower[{i}]={lower[i]:.4f}"
        return True, ""

    def _check_kdj(self, indicator, data):
        k = data.get("k", [])
        d = data.get("d", [])
        j = data.get("j", [])
        if not k or not d or not j:
            return False, "missing k/d/j fields"
        for i in range(len(k)):
            expected_j = 3 * k[i] - 2 * d[i]
            diff = abs(j[i] - expected_j)
            if diff > abs(expected_j) * 0.01 + 1e-8:
                return False, f"j[{i}]={j[i]:.4f} != 3k-2d={expected_j:.4f}"
        return True, ""

    def _check_aroon(self, indicator, data):
        up = data.get("up", [])
        down = data.get("down", [])
        osc = data.get("oscillator", [])
        if not up or not down or not osc:
            return False, "missing up/down/oscillator fields"
        for i in range(len(up)):
            if up[i] < 0 or up[i] > 100:
                return False, f"up[{i}]={up[i]:.4f} out of [0,100]"
            if down[i] < 0 or down[i] > 100:
                return False, f"down[{i}]={down[i]:.4f} out of [0,100]"
            if osc[i] < -100 or osc[i] > 100:
                return False, f"oscillator[{i}]={osc[i]:.4f} out of [-100,100]"
        return True, ""

    def _check_ppo(self, indicator, data):
        values = data.get("values", [])
        signal = data.get("signal", [])
        histogram = data.get("histogram", [])
        if not values or not signal or not histogram:
            return False, "missing values/signal/histogram fields"
        if len(values) != len(signal) or len(values) != len(histogram):
            return False, f"length mismatch: values={len(values)}, signal={len(signal)}, histogram={len(histogram)}"
        for i in range(len(values)):
            expected = values[i] - signal[i]
            diff = abs(histogram[i] - expected)
            if diff > abs(expected) * 0.01 + 1e-8:
                return False, f"histogram[{i}]={histogram[i]:.6f} != values-signal={expected:.6f}"
        return True, ""

    # ----------------------------------------------------------------
    # 4. 批量 POST 测试（仅 crypto + cn）
    # ----------------------------------------------------------------

    def test_batch_indicators(self) -> List[TestResult]:
        """测试 V2 批量指标 POST 接口（crypto 和 cn）"""
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
            cfg = self.markets[market]
            resp = self.client.post_v2_indicators(
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

            results.append(self._make_result(
                f"Batch: {market}",
                "batch_v2",
                TestStatus.PASSED if ok else TestStatus.FAILED,
                f"batch POST {market} - {'OK' if ok else 'FAILED'}",
                resp.response_time_ms,
                resp.error if not resp.success else None,
            ))

        return results

    # ----------------------------------------------------------------
    # helpers
    # ----------------------------------------------------------------

    def _make_result(self, test_name, category, status, message,
                     response_time_ms, error_details=None) -> TestResult:
        result = TestResult(
            test_name=test_name,
            category=category,
            status=status,
            message=message,
            response_time_ms=response_time_ms,
            error_details=error_details,
        )
        self._record_result(result)
        return result

    # ----------------------------------------------------------------
    # 主入口
    # ----------------------------------------------------------------

    def run_all_tests(self) -> Dict:
        """运行所有 V2 指标测试"""
        self.start_test_run()

        self._log("\n" + "=" * 40)
        self._log("V2 Indicator Validation Tests")
        self._log("=" * 40)
        self.test_validation()

        self._log("\n" + "=" * 40)
        self._log("V2 Indicator Functional Tests (27 × 4)")
        self._log("=" * 40)
        self.test_all_indicators_all_markets()

        self._log("\n" + "=" * 40)
        self._log("V2 Indicator Value Sanity Tests (27 × crypto)")
        self._log("=" * 40)
        self.test_indicator_value_sanity()

        self._log("\n" + "=" * 40)
        self._log("V2 Batch Indicator Tests")
        self._log("=" * 40)
        self.test_batch_indicators()

        self.end_test_run()

        return {
            "summary": {
                "total": self.summary.total_tests,
                "passed": self.summary.passed,
                "failed": self.summary.failed,
                "success_rate": self.summary.success_rate,
            },
            "results": [r.to_dict() for r in self.results],
        }


if __name__ == "__main__":
    tester = V2IndicatorTester()
    try:
        tester.run_all_tests()
        tester.generate_report("v2_indicator_test")
    finally:
        tester.close()
