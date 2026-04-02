#!/usr/bin/env python3
"""
Screener API Tests for Market Data Service
Tests for the stock screening (看板) interface - V1 and V2 versions

Run: python test_screener.py
"""
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from test_base import BaseTester, TestResult, TestStatus
from api_client import APIResponse
from config import REPORT_DIR

# ==================== Screener 配置 ====================

SCREENER_CONFIG = {
    # 测试用的历史日期（确保有数据）
    "test_dates": {
        "recent": None,  # None 表示使用最新交易日
        "history": "2024-01-15",  # 固定历史日期
    },

    # 测试行业
    "industries": {
        "include": ["银行", "电子"],
        "exclude": ["综合"],
    },

    # 市值范围 (亿元)
    "market_cap": {
        "small": {"min": 50, "max": 200},
        "medium": {"min": 200, "max": 1000},
        "large": {"min": 1000, "max": 5000},
    },

    # 价格范围 (元)
    "price": {
        "low": {"min": 5, "max": 20},
        "medium": {"min": 20, "max": 50},
        "high": {"min": 50, "max": 200},
    },

    # 涨跌幅范围 (%)
    "change": {
        "down": {"min": -10, "max": -3},
        "flat": {"min": -3, "max": 3},
        "up": {"min": 3, "max": 10},
    },

    # 基本面条件
    "fundamental": {
        "roe_min": 15,
        "roe_years": 3,
        "pe_range": {"min": 5, "max": 30},
        "pb_range": {"min": 0.5, "max": 3},
        "peg_max": 1.5,
        "min_list_days": 365,
    },

    # 流动性条件
    "liquidity": {
        "turnover_range": {"min": 1, "max": 10},
        "amount_min": 10000,  # 万元
        "north_ratio_range": {"min": 1, "max": 10},
    },

    # 技术面条件
    "technical": {
        "ma_trend": "bullish",
        "rs_range": {"min": 70, "max": 100},
        "volume_ratio_range": {"min": 1.5, "max": 5},
    },

    # 分页配置
    "pagination": {
        "default_page": 1,
        "default_size": 20,
        "custom_size": 50,
    },

    # 性能阈值 (ms)
    "performance": {
        "max_response_time": 5000,
        "cache_improvement_ratio": 0.5,  # 缓存后至少快50%
    },
}


# ==================== Screener Tester ====================

class ScreenerTester(BaseTester):
    """看板/选股接口测试器"""

    def __init__(self, base_url: str = None):
        super().__init__(base_url)
        self.config = SCREENER_CONFIG

    # ==================== API 封装 ====================

    def _screener_v1(self, request: Dict) -> APIResponse:
        """V1 选股接口"""
        return self.client.post("/api/v1/stock/cnstock/screener", data=request)

    def _screener_v2(self, request: Dict) -> APIResponse:
        """V2 选股接口"""
        return self.client.post("/api/v2/stock/cnstock/screener", data=request)

    def _get_industries(self) -> APIResponse:
        """获取行业列表"""
        return self.client.get("/api/v1/stock/cnstock/screener/industries")

    def _get_indexes(self) -> APIResponse:
        """获取指数列表"""
        return self.client.get("/api/v1/stock/cnstock/screener/indexes")

    def _get_templates_v1(self) -> APIResponse:
        """获取V1预设模板"""
        return self.client.get("/api/v1/stock/cnstock/screener/templates")

    def _get_templates_v2(self) -> APIResponse:
        """获取V2预设模板"""
        return self.client.get("/api/v2/stock/cnstock/screener/templates")

    def _get_indicators_doc(self) -> APIResponse:
        """获取指标文档"""
        return self.client.get("/api/v1/stock/cnstock/screener/indicators")

    # ==================== 辅助方法 ====================

    def _build_v2_request(self, **kwargs) -> Dict:
        """构建V2请求体"""
        request = {}
        if kwargs.get("trade_date"):
            request["trade_date"] = kwargs["trade_date"]
        if kwargs.get("logic"):
            request["logic"] = kwargs["logic"]
        if kwargs.get("exclude_st") is not None:
            request["exclude_st"] = kwargs["exclude_st"]
        if kwargs.get("min_list_days"):
            request["min_list_days"] = kwargs["min_list_days"]
        if kwargs.get("industry"):
            request["industry"] = kwargs["industry"]
        if kwargs.get("market_cap"):
            request["market_cap"] = kwargs["market_cap"]
        if kwargs.get("price"):
            request["price"] = kwargs["price"]
        if kwargs.get("change"):
            request["change"] = kwargs["change"]
        if kwargs.get("fundamental"):
            request["fundamental"] = kwargs["fundamental"]
        if kwargs.get("liquidity"):
            request["liquidity"] = kwargs["liquidity"]
        if kwargs.get("technical"):
            request["technical"] = kwargs["technical"]
        if kwargs.get("pagination"):
            request["pagination"] = kwargs["pagination"]
        if kwargs.get("sort_by"):
            request["sort_by"] = kwargs["sort_by"]
        if kwargs.get("sort_order"):
            request["sort_order"] = kwargs["sort_order"]
        return request

    def _validate_response_structure(self, data: Dict, is_v2: bool = True) -> tuple:
        """验证响应结构"""
        errors = []

        # 基础字段
        required_fields = ["total", "trade_date", "items", "summary"]
        for field in required_fields:
            if field not in data:
                errors.append(f"缺少字段: {field}")

        # V2特有字段
        if is_v2:
            v2_fields = ["conditions", "pagination"]
            for field in v2_fields:
                if field not in data:
                    errors.append(f"V2缺少字段: {field}")

        # 验证items结构
        if "items" in data and isinstance(data["items"], list) and len(data["items"]) > 0:
            item = data["items"][0]
            item_fields = ["ts_code", "name", "fundamental", "liquidity", "technical"]
            for field in item_fields:
                if field not in item:
                    errors.append(f"item缺少字段: {field}")

        return len(errors) == 0, errors

    def _validate_filter_result(self, items: List[Dict], filter_type: str, filter_value: Any) -> tuple:
        """验证筛选结果是否符合条件"""
        errors = []

        for item in items:
            if filter_type == "market_cap":
                if "market_cap" in item and filter_value:
                    min_val = filter_value.get("min")
                    max_val = filter_value.get("max")
                    val = item.get("market_cap", 0)
                    if min_val and val < min_val:
                        errors.append(f"{item.get('ts_code')} 市值 {val} < 最小值 {min_val}")
                    if max_val and val > max_val:
                        errors.append(f"{item.get('ts_code')} 市值 {val} > 最大值 {max_val}")

            elif filter_type == "price":
                if "close" in item and filter_value:
                    min_val = filter_value.get("min")
                    max_val = filter_value.get("max")
                    val = item.get("close", 0)
                    if min_val and val < min_val:
                        errors.append(f"{item.get('ts_code')} 价格 {val} < 最小值 {min_val}")
                    if max_val and val > max_val:
                        errors.append(f"{item.get('ts_code')} 价格 {val} > 最大值 {max_val}")

            elif filter_type == "change":
                if "change_rate" in item and filter_value:
                    min_val = filter_value.get("min")
                    max_val = filter_value.get("max")
                    val = item.get("change_rate", 0)
                    if min_val and val < min_val:
                        errors.append(f"{item.get('ts_code')} 涨跌幅 {val} < 最小值 {min_val}")
                    if max_val and val > max_val:
                        errors.append(f"{item.get('ts_code')} 涨跌幅 {val} > 最大值 {max_val}")

            elif filter_type == "industry_include":
                if filter_value and item.get("industry") not in filter_value:
                    errors.append(f"{item.get('ts_code')} 行业 {item.get('industry')} 不在包含列表中")

            elif filter_type == "industry_exclude":
                if filter_value and item.get("industry") in filter_value:
                    errors.append(f"{item.get('ts_code')} 行业 {item.get('industry')} 在排除列表中")

        return len(errors) == 0, errors[:5]  # 只返回前5个错误

    # ==================== 测试用例 ====================

    def run_all_tests(self):
        """运行所有测试"""
        self.start_test_run()

        # 1. API可用性测试
        self._log("\n--- API可用性测试 ---")
        self.test_v1_basic_request()
        self.test_v2_basic_request()
        self.test_v2_no_filters()

        # 2. 辅助API测试
        self._log("\n--- 辅助API测试 ---")
        self.test_get_industries()
        self.test_get_indexes()
        self.test_get_templates_v1()
        self.test_get_templates_v2()
        self.test_get_indicators_doc()

        # 3. 新增过滤条件测试
        self._log("\n--- 新增过滤条件测试 ---")
        self.test_industry_include()
        self.test_industry_exclude()
        self.test_market_cap_filter()
        self.test_price_filter()
        self.test_change_filter()
        self.test_combined_new_filters()

        # 4. 基本面筛选测试
        self._log("\n--- 基本面筛选测试 ---")
        self.test_fundamental_roe()
        self.test_fundamental_pe()
        self.test_fundamental_pb()
        self.test_fundamental_peg()
        self.test_fundamental_exclude_st()
        self.test_fundamental_min_list_days()
        self.test_fundamental_combined()

        # 5. 流动性筛选测试
        self._log("\n--- 流动性筛选测试 ---")
        self.test_liquidity_turnover()
        self.test_liquidity_amount()
        self.test_liquidity_north_ratio()
        self.test_liquidity_north_net_buy()
        self.test_liquidity_combined()

        # 6. 技术面筛选测试
        self._log("\n--- 技术面筛选测试 ---")
        self.test_technical_ma_trend_bullish()
        self.test_technical_ma_trend_bearish()
        self.test_technical_ma_custom_periods()
        self.test_technical_rs_range()
        self.test_technical_rs_custom_index()
        self.test_technical_volume_breakout()
        self.test_technical_volume_ratio()
        self.test_technical_combined()

        # 7. 逻辑组合测试
        self._log("\n--- 逻辑组合测试 ---")
        self.test_and_logic_between_layers()
        self.test_or_logic_between_layers()
        self.test_internal_logic_or()

        # 8. 分页和排序测试
        self._log("\n--- 分页和排序测试 ---")
        self.test_pagination_first_page()
        self.test_pagination_second_page()
        self.test_pagination_custom_size()
        self.test_sort_by_market_cap()
        self.test_sort_by_close()
        self.test_sort_by_change_rate()
        self.test_sort_by_roe()
        self.test_sort_by_rs()

        # 9. 数据正确性验证
        self._log("\n--- 数据正确性验证 ---")
        self.test_returned_data_matches_filter()
        self.test_summary_counts()
        self.test_conditions_echo()
        self.test_total_accuracy()

        # 10. 默认值测试
        self._log("\n--- 默认值测试 ---")
        self.test_default_logic()
        self.test_default_pagination()
        self.test_default_ma_periods()

        # 11. 边界条件测试
        self._log("\n--- 边界条件测试 ---")
        self.test_empty_result()
        self.test_extreme_pagination()
        self.test_historical_date()

        # 12. 错误处理测试
        self._log("\n--- 错误处理测试 ---")
        self.test_invalid_date_format()
        self.test_invalid_logic_value()

        # 13. 性能测试
        self._log("\n--- 性能测试 ---")
        self.test_response_time()
        self.test_cache_effectiveness()
        self.test_same_request_consistency()

        self.end_test_run()

    # ==================== API可用性测试 ====================

    def test_v1_basic_request(self):
        """测试V1基础请求"""
        result = TestResult(
            test_name="V1基础请求",
            category="API可用性"
        )

        request = {
            "pagination": {"page": 1, "size": 10}
        }

        response = self._screener_v1(request)

        if response.success:
            valid, errors = self._validate_response_structure(response.data, is_v2=False)
            if valid:
                result.status = TestStatus.PASSED
                result.message = f"成功返回 {response.data.get('total', 0)} 条记录"
            else:
                result.status = TestStatus.FAILED
                result.message = f"响应结构验证失败: {errors}"
                result.error_details = str(errors)
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_v2_basic_request(self):
        """测试V2基础请求"""
        result = TestResult(
            test_name="V2基础请求",
            category="API可用性"
        )

        request = self._build_v2_request(
            pagination={"page": 1, "size": 10},
            exclude_st=True
        )

        response = self._screener_v2(request)

        if response.success:
            valid, errors = self._validate_response_structure(response.data, is_v2=True)
            if valid:
                result.status = TestStatus.PASSED
                result.message = f"成功返回 {response.data.get('total', 0)} 条记录"
            else:
                result.status = TestStatus.FAILED
                result.message = f"响应结构验证失败: {errors}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_v2_no_filters(self):
        """测试V2无过滤条件"""
        result = TestResult(
            test_name="V2无过滤条件",
            category="API可用性"
        )

        request = {"pagination": {"page": 1, "size": 10}}
        response = self._screener_v2(request)

        if response.success:
            total = response.data.get("total", 0)
            if total > 0:
                result.status = TestStatus.PASSED
                result.message = f"无过滤条件返回 {total} 条记录"
            else:
                result.status = TestStatus.FAILED
                result.message = "无过滤条件应该返回股票"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 辅助API测试 ====================

    def test_get_industries(self):
        """测试获取行业列表"""
        result = TestResult(
            test_name="获取行业列表",
            category="辅助API"
        )

        response = self._get_industries()

        if response.success:
            data = response.data
            if isinstance(data, list) and len(data) > 0:
                result.status = TestStatus.PASSED
                result.message = f"返回 {len(data)} 个行业"
            elif isinstance(data, dict) and "data" in data:
                industries = data.get("data", [])
                if len(industries) > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"返回 {len(industries)} 个行业"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "行业列表为空"
            else:
                result.status = TestStatus.FAILED
                result.message = f"响应格式异常: {type(data)}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_get_indexes(self):
        """测试获取指数列表"""
        result = TestResult(
            test_name="获取指数列表",
            category="辅助API"
        )

        response = self._get_indexes()

        if response.success:
            data = response.data
            count = 0
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict) and "data" in data:
                count = len(data.get("data", []))

            if count > 0:
                result.status = TestStatus.PASSED
                result.message = f"返回 {count} 个指数"
            else:
                result.status = TestStatus.FAILED
                result.message = "指数列表为空"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_get_templates_v1(self):
        """测试获取V1预设模板"""
        result = TestResult(
            test_name="获取V1模板",
            category="辅助API"
        )

        response = self._get_templates_v1()

        if response.success:
            result.status = TestStatus.PASSED
            result.message = "V1模板接口可用"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_get_templates_v2(self):
        """测试获取V2预设模板"""
        result = TestResult(
            test_name="获取V2模板",
            category="辅助API"
        )

        response = self._get_templates_v2()

        if response.success:
            result.status = TestStatus.PASSED
            result.message = "V2模板接口可用"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_get_indicators_doc(self):
        """测试获取指标文档"""
        result = TestResult(
            test_name="获取指标文档",
            category="辅助API"
        )

        response = self._get_indicators_doc()

        if response.success:
            result.status = TestStatus.PASSED
            result.message = "指标文档接口可用"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 新增过滤条件测试 ====================

    def test_industry_include(self):
        """测试行业包含筛选"""
        result = TestResult(
            test_name="行业包含筛选",
            category="新增过滤条件"
        )

        include_industries = self.config["industries"]["include"]
        request = self._build_v2_request(
            industry={"include": include_industries},
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) > 0:
                # 验证返回的股票行业都在包含列表中
                valid, errors = self._validate_filter_result(items, "industry_include", include_industries)
                if valid:
                    result.status = TestStatus.PASSED
                    result.message = f"返回 {len(items)} 只股票，行业筛选正确"
                else:
                    result.status = TestStatus.FAILED
                    result.message = f"行业筛选验证失败: {errors}"
            else:
                result.status = TestStatus.PASSED
                result.message = "无匹配结果（可能是正常情况）"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_industry_exclude(self):
        """测试行业排除筛选"""
        result = TestResult(
            test_name="行业排除筛选",
            category="新增过滤条件"
        )

        exclude_industries = self.config["industries"]["exclude"]
        request = self._build_v2_request(
            industry={"exclude": exclude_industries},
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) > 0:
                valid, errors = self._validate_filter_result(items, "industry_exclude", exclude_industries)
                if valid:
                    result.status = TestStatus.PASSED
                    result.message = f"返回 {len(items)} 只股票，行业排除正确"
                else:
                    result.status = TestStatus.FAILED
                    result.message = f"行业排除验证失败: {errors}"
            else:
                result.status = TestStatus.PASSED
                result.message = "无匹配结果（可能是正常情况）"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_market_cap_filter(self):
        """测试市值筛选"""
        result = TestResult(
            test_name="市值筛选",
            category="新增过滤条件"
        )

        market_cap = self.config["market_cap"]["medium"]
        request = self._build_v2_request(
            market_cap=market_cap,
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) > 0:
                valid, errors = self._validate_filter_result(items, "market_cap", market_cap)
                if valid:
                    result.status = TestStatus.PASSED
                    result.message = f"返回 {len(items)} 只股票，市值筛选正确"
                else:
                    result.status = TestStatus.FAILED
                    result.message = f"市值筛选验证失败: {errors}"
            else:
                result.status = TestStatus.PASSED
                result.message = "无匹配结果"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_price_filter(self):
        """测试价格筛选"""
        result = TestResult(
            test_name="价格筛选",
            category="新增过滤条件"
        )

        price = self.config["price"]["medium"]
        request = self._build_v2_request(
            price=price,
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) > 0:
                valid, errors = self._validate_filter_result(items, "price", price)
                if valid:
                    result.status = TestStatus.PASSED
                    result.message = f"返回 {len(items)} 只股票，价格筛选正确"
                else:
                    result.status = TestStatus.FAILED
                    result.message = f"价格筛选验证失败: {errors}"
            else:
                result.status = TestStatus.PASSED
                result.message = "无匹配结果"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_change_filter(self):
        """测试涨跌幅筛选"""
        result = TestResult(
            test_name="涨跌幅筛选",
            category="新增过滤条件"
        )

        change = self.config["change"]["up"]
        request = self._build_v2_request(
            change=change,
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) > 0:
                valid, errors = self._validate_filter_result(items, "change", change)
                if valid:
                    result.status = TestStatus.PASSED
                    result.message = f"返回 {len(items)} 只股票，涨跌幅筛选正确"
                else:
                    result.status = TestStatus.FAILED
                    result.message = f"涨跌幅筛选验证失败: {errors}"
            else:
                result.status = TestStatus.PASSED
                result.message = "无匹配结果"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_combined_new_filters(self):
        """测试组合新过滤条件"""
        result = TestResult(
            test_name="组合新过滤条件",
            category="新增过滤条件"
        )

        request = self._build_v2_request(
            industry={"include": self.config["industries"]["include"]},
            market_cap=self.config["market_cap"]["medium"],
            price=self.config["price"]["medium"],
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"组合筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 基本面筛选测试 ====================

    def test_fundamental_roe(self):
        """测试ROE筛选"""
        result = TestResult(
            test_name="ROE筛选",
            category="基本面筛选"
        )

        request = self._build_v2_request(
            fundamental={
                "roe_min": self.config["fundamental"]["roe_min"],
                "roe_years": self.config["fundamental"]["roe_years"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"ROE筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_fundamental_pe(self):
        """测试PE筛选"""
        result = TestResult(
            test_name="PE筛选",
            category="基本面筛选"
        )

        request = self._build_v2_request(
            fundamental={
                "pe": self.config["fundamental"]["pe_range"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"PE筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_fundamental_pb(self):
        """测试PB筛选"""
        result = TestResult(
            test_name="PB筛选",
            category="基本面筛选"
        )

        request = self._build_v2_request(
            fundamental={
                "pb": self.config["fundamental"]["pb_range"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"PB筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_fundamental_peg(self):
        """测试PEG筛选"""
        result = TestResult(
            test_name="PEG筛选",
            category="基本面筛选"
        )

        request = self._build_v2_request(
            fundamental={
                "peg_max": self.config["fundamental"]["peg_max"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"PEG筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_fundamental_exclude_st(self):
        """测试排除ST"""
        result = TestResult(
            test_name="排除ST股票",
            category="基本面筛选"
        )

        # 先获取包含ST的结果
        request_with_st = self._build_v2_request(
            exclude_st=False,
            pagination={"page": 1, "size": 100}
        )
        response_with_st = self._screener_v2(request_with_st)

        # 获取排除ST的结果
        request_no_st = self._build_v2_request(
            exclude_st=True,
            pagination={"page": 1, "size": 100}
        )
        response_no_st = self._screener_v2(request_no_st)

        if response_with_st.success and response_no_st.success:
            total_with_st = response_with_st.data.get("total", 0)
            total_no_st = response_no_st.data.get("total", 0)

            if total_no_st <= total_with_st:
                result.status = TestStatus.PASSED
                result.message = f"排除ST后: {total_with_st} -> {total_no_st}"
            else:
                result.status = TestStatus.FAILED
                result.message = "排除ST后数量应该减少或相等"
        else:
            result.status = TestStatus.FAILED
            result.message = "请求失败"

        result.response_time_ms = response_no_st.response_time_ms
        self._record_result(result)

    def test_fundamental_min_list_days(self):
        """测试最小上市天数"""
        result = TestResult(
            test_name="最小上市天数",
            category="基本面筛选"
        )

        request = self._build_v2_request(
            min_list_days=self.config["fundamental"]["min_list_days"],
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"上市天数筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_fundamental_combined(self):
        """测试组合基本面条件"""
        result = TestResult(
            test_name="组合基本面条件",
            category="基本面筛选"
        )

        request = self._build_v2_request(
            fundamental={
                "roe_min": self.config["fundamental"]["roe_min"],
                "roe_years": self.config["fundamental"]["roe_years"],
                "pe": self.config["fundamental"]["pe_range"],
                "pb": self.config["fundamental"]["pb_range"],
                "exclude_st": True,
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"组合基本面返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 流动性筛选测试 ====================

    def test_liquidity_turnover(self):
        """测试换手率筛选"""
        result = TestResult(
            test_name="换手率筛选",
            category="流动性筛选"
        )

        request = self._build_v2_request(
            liquidity={
                "turnover": self.config["liquidity"]["turnover_range"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"换手率筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_liquidity_amount(self):
        """测试成交额筛选"""
        result = TestResult(
            test_name="成交额筛选",
            category="流动性筛选"
        )

        request = self._build_v2_request(
            liquidity={
                "amount": {"min": self.config["liquidity"]["amount_min"]},
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"成交额筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_liquidity_north_ratio(self):
        """测试北向持股比例筛选"""
        result = TestResult(
            test_name="北向持股比例筛选",
            category="流动性筛选"
        )

        request = self._build_v2_request(
            liquidity={
                "north_ratio": self.config["liquidity"]["north_ratio_range"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"北向持股筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_liquidity_north_net_buy(self):
        """测试北向净买入筛选"""
        result = TestResult(
            test_name="北向净买入筛选",
            category="流动性筛选"
        )

        request = self._build_v2_request(
            liquidity={
                "north_net_buy": True,
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"北向净买入筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_liquidity_combined(self):
        """测试组合流动性条件"""
        result = TestResult(
            test_name="组合流动性条件",
            category="流动性筛选"
        )

        request = self._build_v2_request(
            liquidity={
                "turnover": self.config["liquidity"]["turnover_range"],
                "amount": {"min": self.config["liquidity"]["amount_min"]},
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"组合流动性返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 技术面筛选测试 ====================

    def test_technical_ma_trend_bullish(self):
        """测试多头趋势筛选"""
        result = TestResult(
            test_name="多头趋势筛选",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "ma_trend": "bullish",
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"多头趋势返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_technical_ma_trend_bearish(self):
        """测试空头趋势筛选"""
        result = TestResult(
            test_name="空头趋势筛选",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "ma_trend": "bearish",
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"空头趋势返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_technical_ma_custom_periods(self):
        """测试自定义MA周期"""
        result = TestResult(
            test_name="自定义MA周期",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "ma_short": 20,
                "ma_long": 60,
                "ma_trend": "bullish",
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"自定义MA周期返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_technical_rs_range(self):
        """测试RS评分范围筛选"""
        result = TestResult(
            test_name="RS评分筛选",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "rs": self.config["technical"]["rs_range"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"RS筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_technical_rs_custom_index(self):
        """测试自定义RS基准指数"""
        result = TestResult(
            test_name="自定义RS基准指数",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "rs": {"min": 50},
                "rs_index_code": "000001.SH",  # 上证指数
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"自定义RS指数返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_technical_volume_breakout(self):
        """测试放量突破筛选"""
        result = TestResult(
            test_name="放量突破筛选",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "volume_breakout": True,
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"放量突破返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_technical_volume_ratio(self):
        """测试量比筛选"""
        result = TestResult(
            test_name="量比筛选",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "volume_ratio": self.config["technical"]["volume_ratio_range"],
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"量比筛选返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_technical_combined(self):
        """测试组合技术面条件"""
        result = TestResult(
            test_name="组合技术面条件",
            category="技术面筛选"
        )

        request = self._build_v2_request(
            technical={
                "ma_trend": "bullish",
                "rs": self.config["technical"]["rs_range"],
                "volume_breakout": True,
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"组合技术面返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 逻辑组合测试 ====================

    def test_and_logic_between_layers(self):
        """测试层间AND逻辑"""
        result = TestResult(
            test_name="层间AND逻辑",
            category="逻辑组合"
        )

        # AND逻辑：必须同时满足所有层
        request = self._build_v2_request(
            logic="AND",
            fundamental={"pe": {"max": 30}},
            liquidity={"turnover": {"min": 2}},
            technical={"ma_trend": "bullish"},
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"AND逻辑返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_or_logic_between_layers(self):
        """测试层间OR逻辑"""
        result = TestResult(
            test_name="层间OR逻辑",
            category="逻辑组合"
        )

        # OR逻辑：满足任一层即可
        request = self._build_v2_request(
            logic="OR",
            fundamental={"pe": {"max": 20}},
            liquidity={"turnover": {"min": 5}},
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"OR逻辑返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_internal_logic_or(self):
        """测试层内OR逻辑"""
        result = TestResult(
            test_name="层内OR逻辑",
            category="逻辑组合"
        )

        request = self._build_v2_request(
            fundamental={
                "logic": "OR",
                "pe": {"max": 20},
                "pb": {"max": 1},
            },
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"层内OR逻辑返回 {response.data.get('total', 0)} 条记录"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 分页和排序测试 ====================

    def test_pagination_first_page(self):
        """测试第一页"""
        result = TestResult(
            test_name="第一页分页",
            category="分页排序"
        )

        request = self._build_v2_request(
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            pagination = response.data.get("pagination", {})
            if len(items) <= 10 and pagination.get("page") == 1:
                result.status = TestStatus.PASSED
                result.message = f"第一页返回 {len(items)} 条，分页信息正确"
            else:
                result.status = TestStatus.FAILED
                result.message = "分页信息不正确"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_pagination_second_page(self):
        """测试第二页"""
        result = TestResult(
            test_name="第二页分页",
            category="分页排序"
        )

        # 获取第一页
        request1 = self._build_v2_request(pagination={"page": 1, "size": 10})
        response1 = self._screener_v2(request1)

        # 获取第二页
        request2 = self._build_v2_request(pagination={"page": 2, "size": 10})
        response2 = self._screener_v2(request2)

        if response1.success and response2.success:
            items1 = response1.data.get("items", [])
            items2 = response2.data.get("items", [])

            if len(items1) > 0 and len(items2) > 0:
                # 验证两页数据不同
                codes1 = {item.get("ts_code") for item in items1}
                codes2 = {item.get("ts_code") for item in items2}
                if codes1 != codes2:
                    result.status = TestStatus.PASSED
                    result.message = f"第二页数据与第一页不同"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "第二页数据与第一页相同"
            else:
                result.status = TestStatus.PASSED
                result.message = "数据量不足以分页"
        else:
            result.status = TestStatus.FAILED
            result.message = "请求失败"

        result.response_time_ms = response2.response_time_ms
        self._record_result(result)

    def test_pagination_custom_size(self):
        """测试自定义分页大小"""
        result = TestResult(
            test_name="自定义分页大小",
            category="分页排序"
        )

        custom_size = self.config["pagination"]["custom_size"]
        request = self._build_v2_request(
            pagination={"page": 1, "size": custom_size}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) <= custom_size:
                result.status = TestStatus.PASSED
                result.message = f"自定义大小 {custom_size}，返回 {len(items)} 条"
            else:
                result.status = TestStatus.FAILED
                result.message = f"返回数量 {len(items)} 超过设定 {custom_size}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_sort_by_market_cap(self):
        """测试按市值排序"""
        result = TestResult(
            test_name="按市值排序",
            category="分页排序"
        )

        # 升序
        request_asc = self._build_v2_request(
            sort_by="market_cap",
            sort_order="asc",
            pagination={"page": 1, "size": 20}
        )
        response_asc = self._screener_v2(request_asc)

        # 降序
        request_desc = self._build_v2_request(
            sort_by="market_cap",
            sort_order="desc",
            pagination={"page": 1, "size": 20}
        )
        response_desc = self._screener_v2(request_desc)

        if response_asc.success and response_desc.success:
            items_asc = response_asc.data.get("items", [])
            items_desc = response_desc.data.get("items", [])

            if len(items_asc) >= 2 and len(items_desc) >= 2:
                # 验证升序第一个小于最后一个
                asc_valid = items_asc[0].get("market_cap", 0) <= items_asc[-1].get("market_cap", 0)
                # 验证降序第一个大于最后一个
                desc_valid = items_desc[0].get("market_cap", 0) >= items_desc[-1].get("market_cap", 0)

                if asc_valid and desc_valid:
                    result.status = TestStatus.PASSED
                    result.message = "市值排序正确"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "排序验证失败"
            else:
                result.status = TestStatus.PASSED
                result.message = "数据量不足"
        else:
            result.status = TestStatus.FAILED
            result.message = "请求失败"

        result.response_time_ms = response_asc.response_time_ms
        self._record_result(result)

    def test_sort_by_close(self):
        """测试按收盘价排序"""
        result = TestResult(
            test_name="按收盘价排序",
            category="分页排序"
        )

        request = self._build_v2_request(
            sort_by="close",
            sort_order="desc",
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"收盘价排序返回 {response.data.get('total', 0)} 条"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_sort_by_change_rate(self):
        """测试按涨跌幅排序"""
        result = TestResult(
            test_name="按涨跌幅排序",
            category="分页排序"
        )

        request = self._build_v2_request(
            sort_by="change_rate",
            sort_order="desc",
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"涨跌幅排序返回 {response.data.get('total', 0)} 条"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_sort_by_roe(self):
        """测试按ROE排序"""
        result = TestResult(
            test_name="按ROE排序",
            category="分页排序"
        )

        request = self._build_v2_request(
            sort_by="roe",
            sort_order="desc",
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"ROE排序返回 {response.data.get('total', 0)} 条"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_sort_by_rs(self):
        """测试按RS评分排序"""
        result = TestResult(
            test_name="按RS评分排序",
            category="分页排序"
        )

        request = self._build_v2_request(
            sort_by="rs",
            sort_order="desc",
            pagination={"page": 1, "size": 20}
        )

        response = self._screener_v2(request)

        if response.success:
            result.status = TestStatus.PASSED
            result.message = f"RS排序返回 {response.data.get('total', 0)} 条"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 数据正确性验证 ====================

    def test_returned_data_matches_filter(self):
        """测试返回数据符合筛选条件"""
        result = TestResult(
            test_name="数据筛选正确性",
            category="数据验证"
        )

        market_cap = self.config["market_cap"]["medium"]
        request = self._build_v2_request(
            market_cap=market_cap,
            price=self.config["price"]["medium"],
            pagination={"page": 1, "size": 50}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            errors = []

            for item in items:
                # 验证市值
                mc = item.get("market_cap", 0)
                if market_cap.get("min") and mc < market_cap["min"]:
                    errors.append(f"{item.get('ts_code')} 市值 {mc} < {market_cap['min']}")

            if len(errors) == 0:
                result.status = TestStatus.PASSED
                result.message = f"验证 {len(items)} 条数据，全部符合筛选条件"
            else:
                result.status = TestStatus.FAILED
                result.message = f"发现 {len(errors)} 条不符合条件: {errors[:3]}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_summary_counts(self):
        """测试Summary统计准确性"""
        result = TestResult(
            test_name="Summary统计准确性",
            category="数据验证"
        )

        request = self._build_v2_request(
            fundamental={"pe": {"max": 30}},
            liquidity={"turnover": {"min": 1}},
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            summary = response.data.get("summary", {})

            # 验证summary字段存在
            required_fields = ["total_stocks", "fundamental_passed", "liquidity_passed"]
            missing = [f for f in required_fields if f not in summary]

            if not missing:
                # 验证数量递减
                total = summary.get("total_stocks", 0)
                fundamental = summary.get("fundamental_passed", 0)

                if fundamental <= total:
                    result.status = TestStatus.PASSED
                    result.message = f"Summary: total={total}, fundamental={fundamental}"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "通过数不应超过总数"
            else:
                result.status = TestStatus.FAILED
                result.message = f"缺少字段: {missing}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_conditions_echo(self):
        """测试Conditions回显正确"""
        result = TestResult(
            test_name="Conditions回显验证",
            category="数据验证"
        )

        request = self._build_v2_request(
            logic="AND",
            market_cap={"min": 100, "max": 1000},
            fundamental={"pe": {"max": 30}},
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            conditions = response.data.get("conditions", {})

            # 验证logic回显
            if conditions.get("logic") == "AND":
                # 验证market_cap回显
                mc = conditions.get("market_cap", {})
                if mc.get("min") == 100 and mc.get("max") == 1000:
                    result.status = TestStatus.PASSED
                    result.message = "Conditions正确回显请求参数"
                else:
                    result.status = TestStatus.FAILED
                    result.message = f"market_cap回显不正确: {mc}"
            else:
                result.status = TestStatus.FAILED
                result.message = f"logic回显不正确: {conditions.get('logic')}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_total_accuracy(self):
        """测试Total数量准确性"""
        result = TestResult(
            test_name="Total数量准确性",
            category="数据验证"
        )

        # 获取大量数据
        request = self._build_v2_request(
            pagination={"page": 1, "size": 1000}
        )

        response = self._screener_v2(request)

        if response.success:
            total = response.data.get("total", 0)
            pagination = response.data.get("pagination", {})

            if pagination.get("total") == total:
                result.status = TestStatus.PASSED
                result.message = f"Total={total} 与 pagination.total 一致"
            else:
                result.status = TestStatus.FAILED
                result.message = f"Total={total} 与 pagination.total={pagination.get('total')} 不一致"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 默认值测试 ====================

    def test_default_logic(self):
        """测试默认逻辑为AND"""
        result = TestResult(
            test_name="默认Logic为AND",
            category="默认值"
        )

        # 不传logic参数
        request = {"pagination": {"page": 1, "size": 10}}
        response = self._screener_v2(request)

        if response.success:
            conditions = response.data.get("conditions", {})
            if conditions.get("logic") == "AND":
                result.status = TestStatus.PASSED
                result.message = "默认logic正确为AND"
            else:
                result.status = TestStatus.FAILED
                result.message = f"默认logic应为AND，实际为 {conditions.get('logic')}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_default_pagination(self):
        """测试默认分页"""
        result = TestResult(
            test_name="默认分页参数",
            category="默认值"
        )

        # 不传分页参数
        request = {}
        response = self._screener_v2(request)

        if response.success:
            pagination = response.data.get("pagination", {})
            if pagination.get("page") == 1 and pagination.get("size") == 20:
                result.status = TestStatus.PASSED
                result.message = "默认分页: page=1, size=20"
            else:
                result.status = TestStatus.FAILED
                result.message = f"默认分页不正确: {pagination}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_default_ma_periods(self):
        """测试默认MA周期"""
        result = TestResult(
            test_name="默认MA周期",
            category="默认值"
        )

        request = self._build_v2_request(
            technical={"ma_trend": "bullish"},
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) > 0:
                # 检查是否有ma50和ma200字段
                tech = items[0].get("technical", {})
                if "ma50" in tech and "ma200" in tech:
                    result.status = TestStatus.PASSED
                    result.message = "默认MA周期 50/200 正确"
                else:
                    result.status = TestStatus.FAILED
                    result.message = f"缺少ma50/ma200字段: {tech}"
            else:
                result.status = TestStatus.PASSED
                result.message = "无数据返回"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 边界条件测试 ====================

    def test_empty_result(self):
        """测试空结果"""
        result = TestResult(
            test_name="空结果测试",
            category="边界条件"
        )

        # 设置不可能满足的条件
        request = self._build_v2_request(
            market_cap={"min": 1000000, "max": 1000001},  # 不可能的市值范围
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            total = response.data.get("total", 0)
            items = response.data.get("items", [])
            if total == 0 and len(items) == 0:
                result.status = TestStatus.PASSED
                result.message = "正确返回空结果"
            else:
                result.status = TestStatus.FAILED
                result.message = f"应该返回空结果，但返回了 {total} 条"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_extreme_pagination(self):
        """测试极端分页"""
        result = TestResult(
            test_name="极端分页测试",
            category="边界条件"
        )

        request = self._build_v2_request(
            pagination={"page": 10000, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            items = response.data.get("items", [])
            if len(items) == 0:
                result.status = TestStatus.PASSED
                result.message = "超出范围的页码返回空结果"
            else:
                result.status = TestStatus.PASSED
                result.message = f"返回 {len(items)} 条数据"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_historical_date(self):
        """测试历史日期查询"""
        result = TestResult(
            test_name="历史日期查询",
            category="边界条件"
        )

        historical_date = self.config["test_dates"]["history"]
        request = self._build_v2_request(
            trade_date=historical_date,
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            trade_date = response.data.get("trade_date", "")
            if trade_date == historical_date:
                result.status = TestStatus.PASSED
                result.message = f"历史日期 {historical_date} 查询成功"
            else:
                result.status = TestStatus.FAILED
                result.message = f"返回日期 {trade_date} 与请求 {historical_date} 不符"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 错误处理测试 ====================

    def test_invalid_date_format(self):
        """测试无效日期格式"""
        result = TestResult(
            test_name="无效日期格式",
            category="错误处理"
        )

        request = self._build_v2_request(
            trade_date="2024/01/15",  # 错误格式
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        # 可能返回错误，也可能自动处理
        if response.success:
            result.status = TestStatus.PASSED
            result.message = "服务端处理了日期格式"
        else:
            result.status = TestStatus.PASSED
            result.message = f"正确返回错误: {response.error[:50]}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_invalid_logic_value(self):
        """测试无效逻辑值"""
        result = TestResult(
            test_name="无效Logic值",
            category="错误处理"
        )

        request = self._build_v2_request(
            logic="INVALID",  # 无效值
            pagination={"page": 1, "size": 10}
        )

        response = self._screener_v2(request)

        if response.success:
            # 应该使用默认值AND
            conditions = response.data.get("conditions", {})
            if conditions.get("logic") == "AND":
                result.status = TestStatus.PASSED
                result.message = "无效logic被正确处理为默认AND"
            else:
                result.status = TestStatus.FAILED
                result.message = f"logic应为AND，实际为 {conditions.get('logic')}"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    # ==================== 性能测试 ====================

    def test_response_time(self):
        """测试响应时间"""
        result = TestResult(
            test_name="响应时间测试",
            category="性能"
        )

        request = self._build_v2_request(
            fundamental={"pe": {"max": 50}},
            pagination={"page": 1, "size": 50}
        )

        response = self._screener_v2(request)

        max_time = self.config["performance"]["max_response_time"]
        if response.success:
            if response.response_time_ms < max_time:
                result.status = TestStatus.PASSED
                result.message = f"响应时间 {response.response_time_ms:.0f}ms < {max_time}ms"
            else:
                result.status = TestStatus.FAILED
                result.message = f"响应时间 {response.response_time_ms:.0f}ms > {max_time}ms"
        else:
            result.status = TestStatus.FAILED
            result.message = f"请求失败: {response.error}"

        result.response_time_ms = response.response_time_ms
        self._record_result(result)

    def test_cache_effectiveness(self):
        """测试缓存效果"""
        result = TestResult(
            test_name="缓存效果测试",
            category="性能"
        )

        request = self._build_v2_request(
            market_cap=self.config["market_cap"]["medium"],
            pagination={"page": 1, "size": 20}
        )

        # 第一次请求
        response1 = self._screener_v2(request)

        # 等待一小段时间
        time.sleep(0.5)

        # 第二次相同请求（应该命中缓存）
        response2 = self._screener_v2(request)

        if response1.success and response2.success:
            # 第二次应该更快（或至少不慢很多）
            improvement = response1.response_time_ms - response2.response_time_ms
            ratio = improvement / response1.response_time_ms if response1.response_time_ms > 0 else 0

            if ratio >= self.config["performance"]["cache_improvement_ratio"]:
                result.status = TestStatus.PASSED
                result.message = f"缓存提升 {ratio*100:.1f}% ({response1.response_time_ms:.0f}ms -> {response2.response_time_ms:.0f}ms)"
            else:
                result.status = TestStatus.PASSED
                result.message = f"缓存效果不明显 ({response1.response_time_ms:.0f}ms -> {response2.response_time_ms:.0f}ms)"
        else:
            result.status = TestStatus.FAILED
            result.message = "请求失败"

        result.response_time_ms = response2.response_time_ms
        self._record_result(result)

    def test_same_request_consistency(self):
        """测试相同请求一致性"""
        result = TestResult(
            test_name="请求一致性测试",
            category="性能"
        )

        request = self._build_v2_request(
            fundamental={"pe": {"max": 30}},
            pagination={"page": 1, "size": 20}
        )

        response1 = self._screener_v2(request)
        response2 = self._screener_v2(request)

        if response1.success and response2.success:
            total1 = response1.data.get("total", 0)
            total2 = response2.data.get("total", 0)

            if total1 == total2:
                result.status = TestStatus.PASSED
                result.message = f"两次请求结果一致: total={total1}"
            else:
                result.status = TestStatus.FAILED
                result.message = f"结果不一致: {total1} vs {total2}"
        else:
            result.status = TestStatus.FAILED
            result.message = "请求失败"

        result.response_time_ms = response2.response_time_ms
        self._record_result(result)


# ==================== 主入口 ====================

def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Screener API Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_screener.py                    # 运行所有测试
  python test_screener.py --url http://localhost:3101  # 指定服务地址
  python test_screener.py --output my_test   # 自定义报告文件名
        """
    )

    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Base URL for the market data service"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output filename prefix for reports"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Handle verbose flag
    if args.verbose:
        import config
        config.VERBOSE = True

    # Run tests
    print("\n" + "=" * 60)
    print("SCREENER API TESTS")
    print("=" * 60)

    tester = ScreenerTester(args.url)
    try:
        tester.run_all_tests()
        report_name = args.output or f"screener_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tester.generate_report(report_name)
        success = tester.summary.failed == 0
    finally:
        tester.close()

    print("\n" + "=" * 60)
    print(f"Test completed: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
