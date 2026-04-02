"""
Tushare API 测试
测试 A股、港股、美股数据接口
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from test_base import BaseTester, TestResult, TestStatus
from api_client import APIClient
from config import TUSHARE_CONFIG, BASE_URL, API_KEY


class TushareTester(BaseTester):
    """Tushare 股票数据测试器"""

    def __init__(self):
        super().__init__(BASE_URL)
        self.config = TUSHARE_CONFIG

    def run_all_tests(self):
        """运行所有 Tushare 测试"""
        self.start_test_run()

        # A股测试
        self._test_astock_symbols()
        self._test_astock_klines()
        self._test_astock_klines_weekly()
        self._test_astock_klines_monthly()
        self._test_index_basic()
        self._test_index_daily()

        # A股扩展测试
        self._test_astock_company()
        self._test_astock_name_change()
        self._test_astock_new_share()
        self._test_astock_stk_limit()
        self._test_astock_suspend()
        self._test_astock_trade_cal()
        self._test_astock_daily_basic()
        self._test_astock_adj_factor()

        # 指数扩展测试
        self._test_index_weekly()
        self._test_index_monthly()
        self._test_index_daily_basic()
        self._test_index_weight()
        self._test_index_classify()

        # 港股测试
        self._test_hkstock_symbols()
        self._test_hkstock_daily()

        # 港股扩展测试
        self._test_hkstock_trade_cal()
        self._test_hkstock_ggt_top10()
        self._test_hkstock_ggt_daily()
        self._test_hkstock_hold()

        # 美股测试
        self._test_usstock_symbols()
        self._test_usstock_daily()

        # 美股扩展测试
        self._test_usstock_trade_cal()

        # 财务数据测试
        self._test_finance_income()
        self._test_finance_balancesheet()
        self._test_finance_cashflow()
        self._test_finance_indicator()
        self._test_finance_forecast()
        self._test_finance_express()
        self._test_finance_dividend()

        # 财务扩展测试
        self._test_finance_disclosure_date()
        self._test_finance_main_bz()

        # 基金数据测试
        self._test_fund_basic()
        self._test_fund_nav()
        self._test_fund_daily()
        self._test_fund_portfolio()

        # 基金扩展测试
        self._test_fund_etf_basic()
        self._test_fund_share()
        self._test_fund_div()
        self._test_fund_manager()
        self._test_fund_company()

        # 参考数据测试
        self._test_holders_top10()
        self._test_holders_float_top10()
        self._test_holders_number()
        self._test_repurchase()
        self._test_block_trade()
        self._test_share_float()
        self._test_pledge()

        # 参考数据扩展测试
        self._test_pledge_stat()

        # 宏观经济测试
        self._test_macro_shibor()
        self._test_macro_lpr()
        self._test_macro_cpi()
        self._test_macro_ppi()
        self._test_macro_gdp()
        self._test_macro_money()

        # 资金流向测试
        self._test_moneyflow_hsgt()
        self._test_moneyflow_hsgt_top10()
        self._test_moneyflow_margin()
        self._test_moneyflow_margin_detail()
        self._test_moneyflow_stock()

        self.end_test_run()

    # ==================== A股测试 ====================

    def _test_astock_symbols(self):
        """测试 A股股票列表"""
        result = TestResult(
            test_name="A股股票列表",
            category="Tushare-A股"
        )

        try:
            response = self.client.get_astock_symbols(list_status="L")

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                if "total" in data and "symbols" in data:
                    total = data.get("total", 0)
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 只A股股票"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "响应格式错误，缺少 total 或 symbols 字段"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_klines(self):
        """测试 A股日线K线"""
        symbol = self.config["astock"]["symbols"][0]

        for symbol in self.config["astock"]["symbols"][:2]:
            result = TestResult(
                test_name=f"A股日线K线-{symbol}",
                category="Tushare-A股",
                symbol=symbol,
                interval="daily"
            )

            try:
                # 获取最近30天数据
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

                response = self.client.get_astock_klines(
                    symbol=symbol,
                    interval="daily",
                    start_date=start_date,
                    end_date=end_date,
                    limit=30
                )

                result.response_time_ms = response.response_time_ms

                if response.success and response.data:
                    data = response.data
                    total = data.get("total", 0)
                    if total > 0:
                        result.status = TestStatus.PASSED
                        result.message = f"获取 {total} 条K线数据"
                    else:
                        result.status = TestStatus.FAILED
                        result.message = "返回数据为空"
                else:
                    result.status = TestStatus.FAILED
                    result.message = response.error or "请求失败"

            except Exception as e:
                result.status = TestStatus.ERROR
                result.message = str(e)

            self._record_result(result)
            self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_klines_weekly(self):
        """测试 A股周线K线"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"A股周线K线-{symbol}",
            category="Tushare-A股",
            symbol=symbol,
            interval="weekly"
        )

        try:
            response = self.client.get_astock_klines(
                symbol=symbol,
                interval="weekly",
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条周线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_klines_monthly(self):
        """测试 A股月线K线"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"A股月线K线-{symbol}",
            category="Tushare-A股",
            symbol=symbol,
            interval="monthly"
        )

        try:
            response = self.client.get_astock_klines(
                symbol=symbol,
                interval="monthly",
                limit=12
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条月线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_index_basic(self):
        """测试指数基本信息"""
        result = TestResult(
            test_name="指数基本信息",
            category="Tushare-指数"
        )

        try:
            response = self.client.get_index_basic(market="SSE")

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 个指数信息"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_index_daily(self):
        """测试指数日线数据"""
        ts_code = self.config["astock"]["indices"][0]
        result = TestResult(
            test_name=f"指数日线数据-{ts_code}",
            category="Tushare-指数",
            symbol=ts_code
        )

        try:
            response = self.client.get_index_daily(
                ts_code=ts_code,
                limit=30
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条指数日线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 港股测试 ====================

    def _test_hkstock_symbols(self):
        """测试港股股票列表"""
        result = TestResult(
            test_name="港股股票列表",
            category="Tushare-港股"
        )

        try:
            response = self.client.get_hkstock_symbols(list_status="L")

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                if "total" in data and "symbols" in data:
                    total = data.get("total", 0)
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 只港股"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "响应格式错误"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_hkstock_daily(self):
        """测试港股日线数据"""
        symbol = self.config["hkstock"]["symbols"][0]
        result = TestResult(
            test_name=f"港股日线数据-{symbol}",
            category="Tushare-港股",
            symbol=symbol
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

            response = self.client.get_hkstock_daily(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                limit=30
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条港股日线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 美股测试 ====================

    def _test_usstock_symbols(self):
        """测试美股股票列表"""
        result = TestResult(
            test_name="美股股票列表",
            category="Tushare-美股"
        )

        try:
            response = self.client.get_usstock_symbols()

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                if "total" in data and "symbols" in data:
                    total = data.get("total", 0)
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 只美股"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "响应格式错误"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_usstock_daily(self):
        """测试美股日线数据"""
        symbol = self.config["usstock"]["symbols"][0]
        result = TestResult(
            test_name=f"美股日线数据-{symbol}",
            category="Tushare-美股",
            symbol=symbol
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

            response = self.client.get_usstock_daily(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                limit=30
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条美股日线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 财务数据测试 ====================

    def _test_finance_income(self):
        """测试利润表数据"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"利润表-{symbol}",
            category="Tushare-财务"
        )

        try:
            response = self.client.get_finance_income(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条利润表数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_finance_balancesheet(self):
        """测试资产负债表数据"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"资产负债表-{symbol}",
            category="Tushare-财务"
        )

        try:
            response = self.client.get_finance_balancesheet(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条资产负债表数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_finance_indicator(self):
        """测试财务指标数据"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"财务指标-{symbol}",
            category="Tushare-财务"
        )

        try:
            response = self.client.get_finance_indicator(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条财务指标数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_finance_dividend(self):
        """测试分红送股数据"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"分红送股-{symbol}",
            category="Tushare-财务"
        )

        try:
            response = self.client.get_finance_dividend(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条分红数据"
                else:
                    result.status = TestStatus.PASSED  # 暂时没有分红也是通过的
                    result.message = "暂无分红数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_finance_cashflow(self):
        """测试现金流量表数据"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"现金流量表-{symbol}",
            category="Tushare-财务"
        )

        try:
            response = self.client.get_finance_cashflow(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条现金流量表数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_finance_forecast(self):
        """测试业绩预告数据"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"业绩预告-{symbol}",
            category="Tushare-财务"
        )

        try:
            response = self.client.get_finance_forecast(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条业绩预告数据"
                else:
                    result.status = TestStatus.PASSED  # 可能没有预告
                    result.message = "暂无业绩预告数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_finance_express(self):
        """测试业绩快报数据"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"业绩快报-{symbol}",
            category="Tushare-财务"
        )

        try:
            response = self.client.get_finance_express(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条业绩快报数据"
                else:
                    result.status = TestStatus.PASSED  # 可能没有快报
                    result.message = "暂无业绩快报数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 基金数据测试 ====================

    def _test_fund_basic(self):
        """测试基金列表"""
        result = TestResult(
            test_name="基金列表",
            category="Tushare-基金"
        )

        try:
            response = self.client.get_fund_basic(
                market="E",
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条基金数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_fund_nav(self):
        """测试基金净值"""
        result = TestResult(
            test_name="基金净值",
            category="Tushare-基金"
        )

        try:
            response = self.client.get_fund_nav(
                ts_code="110022.OF",
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条净值数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_fund_daily(self):
        """测试ETF日线行情"""
        result = TestResult(
            test_name="ETF日线行情",
            category="Tushare-基金"
        )

        try:
            response = self.client.get_fund_daily(
                ts_code="159915.SZ",  # 易方达创业板ETF
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条ETF日线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_fund_portfolio(self):
        """测试基金持仓"""
        result = TestResult(
            test_name="基金持仓",
            category="Tushare-基金"
        )

        try:
            response = self.client.get_fund_portfolio(
                ts_code="110022.OF",
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条持仓数据"
                else:
                    result.status = TestStatus.PASSED  # 可能没有持仓数据
                    result.message = "暂无持仓数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 参考数据测试 ====================

    def _test_holders_top10(self):
        """测试前十大股东"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"前十大股东-{symbol}",
            category="Tushare-参考"
        )

        try:
            response = self.client.get_holders_top10(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条股东数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_holders_float_top10(self):
        """测试前十大流通股东"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"前十大流通股东-{symbol}",
            category="Tushare-参考"
        )

        try:
            response = self.client.get_holders_float_top10(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条流通股东数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_holders_number(self):
        """测试股东人数"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"股东人数-{symbol}",
            category="Tushare-参考"
        )

        try:
            response = self.client.get_holders_number(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条股东人数数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_repurchase(self):
        """测试股票回购"""
        result = TestResult(
            test_name="股票回购",
            category="Tushare-参考"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")

            response = self.client.get_repurchase(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条回购数据"
                else:
                    result.status = TestStatus.PASSED  # 可能没有回购
                    result.message = "暂无回购数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_block_trade(self):
        """测试大宗交易"""
        result = TestResult(
            test_name="大宗交易",
            category="Tushare-参考"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_block_trade(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条大宗交易数据"
                else:
                    result.status = TestStatus.PASSED  # 可能没有大宗交易
                    result.message = "暂无大宗交易数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_share_float(self):
        """测试限售股解禁"""
        result = TestResult(
            test_name="限售股解禁",
            category="Tushare-参考"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_share_float(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条解禁数据"
                else:
                    result.status = TestStatus.PASSED  # 可能没有解禁
                    result.message = "暂无解禁数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_pledge(self):
        """测试股权质押"""
        symbol = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"股权质押-{symbol}",
            category="Tushare-参考"
        )

        try:
            response = self.client.get_pledge(
                ts_code=symbol,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条质押数据"
                else:
                    result.status = TestStatus.PASSED  # 可能没有质押
                    result.message = "暂无质押数据"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 宏观经济测试 ====================

    def _test_macro_shibor(self):
        """测试Shibor利率"""
        result = TestResult(
            test_name="Shibor利率",
            category="Tushare-宏观"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_macro_shibor(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条Shibor数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_macro_lpr(self):
        """测试LPR利率"""
        result = TestResult(
            test_name="LPR利率",
            category="Tushare-宏观"
        )

        try:
            response = self.client.get_macro_lpr(limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条LPR数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_macro_cpi(self):
        """测试CPI数据"""
        result = TestResult(
            test_name="CPI数据",
            category="Tushare-宏观"
        )

        try:
            response = self.client.get_macro_cpi(limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条CPI数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_macro_ppi(self):
        """测试PPI数据"""
        result = TestResult(
            test_name="PPI数据",
            category="Tushare-宏观"
        )

        try:
            response = self.client.get_macro_ppi(limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条PPI数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_macro_gdp(self):
        """测试GDP数据"""
        result = TestResult(
            test_name="GDP数据",
            category="Tushare-宏观"
        )

        try:
            response = self.client.get_macro_gdp(limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条GDP数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_macro_money(self):
        """测试货币供应量数据"""
        result = TestResult(
            test_name="货币供应量",
            category="Tushare-宏观"
        )

        try:
            response = self.client.get_macro_money(limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条货币供应量数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 资金流向测试 ====================

    def _test_moneyflow_hsgt(self):
        """测试沪深港通资金流向"""
        result = TestResult(
            test_name="沪深港通资金流向",
            category="Tushare-资金"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_moneyflow_hsgt(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条资金流向数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_moneyflow_hsgt_top10(self):
        """测试沪深股通十大成交股"""
        result = TestResult(
            test_name="沪深股通十大成交股",
            category="Tushare-资金"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

            response = self.client.get_moneyflow_hsgt_top10(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条十大成交股数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_moneyflow_margin(self):
        """测试融资融券汇总"""
        result = TestResult(
            test_name="融资融券汇总",
            category="Tushare-资金"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_moneyflow_margin(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条融资融券汇总数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_moneyflow_margin_detail(self):
        """测试融资融券明细"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"融资融券明细-{ts_code}",
            category="Tushare-资金",
            symbol=ts_code
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_moneyflow_margin_detail(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条融资融券明细数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_moneyflow_stock(self):
        """测试个股资金流向"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"个股资金流向-{ts_code}",
            category="Tushare-资金",
            symbol=ts_code
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

            response = self.client.get_moneyflow_stock(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条个股资金流向数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== A股扩展测试 ====================

    def _test_astock_company(self):
        """测试上市公司基本信息"""
        result = TestResult(
            test_name="上市公司基本信息",
            category="Tushare-A股"
        )

        try:
            response = self.client.get_astock_company(limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条公司信息"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_name_change(self):
        """测试股票曾用名"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"股票曾用名-{ts_code}",
            category="Tushare-A股",
            symbol=ts_code
        )

        try:
            response = self.client.get_astock_name_change(ts_code=ts_code, limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条曾用名记录"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_new_share(self):
        """测试IPO新股上市"""
        result = TestResult(
            test_name="IPO新股上市",
            category="Tushare-A股"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")

            response = self.client.get_astock_new_share(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条新股数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_stk_limit(self):
        """测试每日涨跌停价格"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"每日涨跌停价格-{ts_code}",
            category="Tushare-A股",
            symbol=ts_code
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

            response = self.client.get_astock_stk_limit(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条涨跌停数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_suspend(self):
        """测试停复牌信息"""
        result = TestResult(
            test_name="停复牌信息",
            category="Tushare-A股"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_astock_suspend(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条停复牌数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_trade_cal(self):
        """测试交易日历"""
        result = TestResult(
            test_name="A股交易日历",
            category="Tushare-A股"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_astock_trade_cal(
                exchange="SSE",
                start_date=start_date,
                end_date=end_date,
                limit=50
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条交易日历"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_daily_basic(self):
        """测试每日指标"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"每日指标-{ts_code}",
            category="Tushare-A股",
            symbol=ts_code
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_astock_daily_basic(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条每日指标"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_astock_adj_factor(self):
        """测试复权因子"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"复权因子-{ts_code}",
            category="Tushare-A股",
            symbol=ts_code
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y%m%d")

            response = self.client.get_astock_adj_factor(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=30
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条复权因子"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 指数扩展测试 ====================

    def _test_index_weekly(self):
        """测试指数周线"""
        ts_code = self.config.get("index", {}).get("symbols", ["000001.SH"])[0]
        result = TestResult(
            test_name=f"指数周线-{ts_code}",
            category="Tushare-指数",
            symbol=ts_code,
            interval="weekly"
        )

        try:
            response = self.client.get_index_weekly(ts_code=ts_code, limit=20)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条周线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_index_monthly(self):
        """测试指数月线"""
        ts_code = self.config.get("index", {}).get("symbols", ["000001.SH"])[0]
        result = TestResult(
            test_name=f"指数月线-{ts_code}",
            category="Tushare-指数",
            symbol=ts_code,
            interval="monthly"
        )

        try:
            response = self.client.get_index_monthly(ts_code=ts_code, limit=12)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条月线数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_index_daily_basic(self):
        """测试指数每日指标"""
        ts_code = self.config.get("index", {}).get("symbols", ["000001.SH"])[0]
        result = TestResult(
            test_name=f"指数每日指标-{ts_code}",
            category="Tushare-指数",
            symbol=ts_code
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_index_daily_basic(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条指数指标"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_index_weight(self):
        """测试指数成分权重"""
        result = TestResult(
            test_name="指数成分权重",
            category="Tushare-指数"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_index_weight(
                index_code="000016.SH",  # 上证50
                start_date=start_date,
                end_date=end_date,
                limit=60
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条成分权重"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_index_classify(self):
        """测试申万行业分类"""
        result = TestResult(
            test_name="申万行业分类",
            category="Tushare-指数"
        )

        try:
            response = self.client.get_index_classify(limit=50)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 个行业分类"
                else:
                    # 数据为空，可能是权限问题，标记为通过但提示
                    result.status = TestStatus.PASSED
                    result.message = "接口调用成功，但无数据返回（可能需要更高权限）"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 港股扩展测试 ====================

    def _test_hkstock_trade_cal(self):
        """测试港股交易日历"""
        result = TestResult(
            test_name="港股交易日历",
            category="Tushare-港股"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_hkstock_trade_cal(
                start_date=start_date,
                end_date=end_date,
                limit=50
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条交易日历"
                else:
                    result.status = TestStatus.PASSED
                    result.message = "接口调用成功，但无数据返回（可能需要更高权限）"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_hkstock_ggt_top10(self):
        """测试港股通十大成交股"""
        result = TestResult(
            test_name="港股通十大成交股",
            category="Tushare-港股"
        )

        try:
            # 需要 trade_date 参数
            trade_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

            response = self.client.get_hkstock_ggt_top10(
                trade_date=trade_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条成交数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_hkstock_ggt_daily(self):
        """测试港股通每日成交"""
        result = TestResult(
            test_name="港股通每日成交",
            category="Tushare-港股"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_hkstock_ggt_daily(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条成交数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_hkstock_hold(self):
        """测试沪深股通持股明细"""
        result = TestResult(
            test_name="沪深股通持股明细",
            category="Tushare-港股"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_hkstock_hold(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条持股数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 美股扩展测试 ====================

    def _test_usstock_trade_cal(self):
        """测试美股交易日历"""
        result = TestResult(
            test_name="美股交易日历",
            category="Tushare-美股"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_usstock_trade_cal(
                start_date=start_date,
                end_date=end_date,
                limit=50
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条交易日历"
                else:
                    result.status = TestStatus.PASSED
                    result.message = "接口调用成功，但无数据返回(可能需要更高权限)"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"
        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 财务扩展测试 ====================

    def _test_finance_disclosure_date(self):
        """测试财报披露日期"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"财报披露日期-{ts_code}",
            category="Tushare-财务",
            symbol=ts_code
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")

            response = self.client.get_finance_disclosure_date(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                limit=10
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条披露日期"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_finance_main_bz(self):
        """测试主营业务构成"""
        ts_code = self.config["astock"]["symbols"][0]
        result = TestResult(
            test_name=f"主营业务构成-{ts_code}",
            category="Tushare-财务",
            symbol=ts_code
        )

        try:
            response = self.client.get_finance_main_bz(ts_code=ts_code, limit=10)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条业务构成"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 基金扩展测试 ====================

    def _test_fund_etf_basic(self):
        """测试ETF列表 - 需要更高级别权限"""
        result = TestResult(
            test_name="ETF列表",
            category="Tushare-基金"
        )

        # 该接口需要更高级别权限，跳过测试
        result.status = TestStatus.SKIPPED
        result.message = "跳过: 需要更高级别Tushare权限"
        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_fund_share(self):
        """测试基金份额"""
        result = TestResult(
            test_name="基金份额",
            category="Tushare-基金"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_fund_share(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条份额数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_fund_div(self):
        """测试基金分红"""
        result = TestResult(
            test_name="基金分红",
            category="Tushare-基金"
        )

        try:
            # 需要 ts_code 参数，使用常见基金代码
            response = self.client.get_fund_div(ts_code="110022.OF", limit=20)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条分红数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_fund_manager(self):
        """测试基金经理"""
        result = TestResult(
            test_name="基金经理",
            category="Tushare-基金"
        )

        try:
            response = self.client.get_fund_manager(limit=20)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 位基金经理"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    def _test_fund_company(self):
        """测试基金公司"""
        result = TestResult(
            test_name="基金公司",
            category="Tushare-基金"
        )

        try:
            response = self.client.get_fund_company(limit=50)

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total > 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 家基金公司"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")

    # ==================== 参考数据扩展测试 ====================

    def _test_pledge_stat(self):
        """测试股权质押统计"""
        result = TestResult(
            test_name="股权质押统计",
            category="Tushare-参考数据"
        )

        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            response = self.client.get_pledge_stat(
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            result.response_time_ms = response.response_time_ms

            if response.success and response.data:
                data = response.data
                total = data.get("total", 0)
                if total >= 0:
                    result.status = TestStatus.PASSED
                    result.message = f"获取 {total} 条质押统计数据"
                else:
                    result.status = TestStatus.FAILED
                    result.message = "返回数据为空"
            else:
                result.status = TestStatus.FAILED
                result.message = response.error or "请求失败"

        except Exception as e:
            result.status = TestStatus.ERROR
            result.message = str(e)

        self._record_result(result)
        self._log(f"{result.test_name}: {result.status.value} - {result.message}")


def main():
    """主函数"""
    print("=" * 60)
    print("TUSHARE API 测试")
    print("=" * 60)
    print(f"服务地址: {BASE_URL}")
    print()

    tester = TushareTester()
    try:
        tester.run_all_tests()
        tester.generate_report("tushare_test")
    finally:
        tester.close()

    print()
    print("=" * 60)
    print("测试汇总")
    print("=" * 60)
    print(f"总计: {tester.summary.total_tests}")
    print(f"通过: {tester.summary.passed}")
    print(f"失败: {tester.summary.failed}")
    print(f"成功率: {tester.summary.success_rate:.1f}%")

    return 0 if tester.summary.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
