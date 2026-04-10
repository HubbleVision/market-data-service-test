# K线数据质量校验模块

> 模块路径: `tests/v2/07_kline_quality/`
> 创建时间: 2026-04-05
> 运行方式: `python scripts/run_v2.py -m kline_quality`

---

## 一、模块概述

对 A股、港股、美股的日线 K线数据进行质量校验，确保数据的完整性和准确性。覆盖 5 项校验，异常时自动与第三方数据源交叉验证。

---

## 二、校验项说明

### 2.1 OHLC 结构校验 (`test_ohlc_structure`)

校验每根 K线的 OHLC 基础结构是否合法：

| 检查项 | 规则 | 说明 |
|--------|------|------|
| 字段完整 | open/high/low/close/volume 均不为 null | 缺失任一字段即报错 |
| 价格为正 | open > 0, close > 0 | 价格不能为零或负数 |
| high >= low | high >= low | 最高价不能低于最低价 |
| high 包含 open/close | high >= open, high >= close | 最高价应覆盖开盘和收盘 |
| low 包含 open/close | low <= open, low <= close | 最低价应覆盖开盘和收盘 |
| volume 合法 | volume >= 0 | 成交量不能为负 |

### 2.2 价格异常检测 (`test_price_change`)

检测日间价格变化是否超过市场合理阈值：

| 市场 | 阈值 | 说明 |
|------|------|------|
| A股 (cn) | ±30% | 主板 ±10%，科创/创业板 ±20%，新股不设限，30% 兜底 |
| 港股 (hk) | ±50% | 无涨跌停限制，50%+ 极为罕见 |
| 美股 (us) | ±40% | 无涨跌停限制，40%+ 极为罕见 |

**特殊处理**: A股数据支持 `adjFactor`（复权因子），使用调整后的价格 `close * adjFactor` 计算涨跌幅，避免除权除息造成误报。

### 2.3 成交量异常检测 (`test_volume_anomaly`)

基于近 20 日均量检测成交量异常：

| 异常类型 | 规则 | 说明 |
|---------|------|------|
| 放量异常 | 当前成交量 > 20日均量 × 15 倍 | 剔除停牌复牌首日等特殊情况 |
| 零成交异常 | volume=0 且 open != close | 有价格变动但无成交，数据矛盾 |

**前置条件**: 需要至少 21 根 K线数据（20根计算均量 + 1根检测）。

### 2.4 数据新鲜度校验 (`test_data_freshness`)

检查最新 K线数据的时效性：

| 配置项 | 值 | 说明 |
|--------|---|------|
| 最大延迟 | 2 个自然日 | 最新K线日期距今天不超过 2 天 |

**说明**: 考虑周末和节假日，2 天容忍度可在正常交易日保证数据及时更新。

### 2.5 第三方交叉验证 (`test_cross_verify`)

当价格异常检测发现异常时，自动向第三方数据源查询验证：

| 市场 | 数据源 | 说明 |
|------|--------|------|
| A股 | 新浪财经 (hq.sinajs.cn) | 通过 `sz000001` 格式查询实时数据 |
| 港股/美股 | Yahoo Finance (yfinance) | 通过 `yfinance` 库查询历史数据 |

**判定规则**: 第三方价格与本地价格差异 < 2% 则视为数据正确（真实市场波动），> 2% 则确认数据异常。

**依赖**: 港股/美股交叉验证需要安装 `yfinance`（`pip install yfinance pandas`），未安装时标记为 SKIP。

---

## 三、测试标的

从 `config.py` 的 `TUSHARE_CONFIG` 自动读取：

| 市场 | 标的 | 来源 |
|------|------|------|
| CN | 000001.SZ, 600000.SH | TUSHARE_CONFIG.astock.symbols |
| HK | 00700.HK, 00941.HK | TUSHARE_CONFIG.hkstock.symbols |
| US | AAPL, MSFT, GOOGL | TUSHARE_CONFIG.usstock.symbols |

---

## 四、数据获取方式

| 市场 | API 端点 | 参数 |
|------|---------|------|
| CN | `/api/v2/cnstock/klines` | interval=daily, limit=60 |
| HK | `/api/v2/hkstock/stocks` | limit=60 |
| US | `/api/v2/usstock/stocks` | limit=60 |

---

## 五、输出说明

每项校验对每个标的输出一条结果：

| 状态 | 含义 |
|------|------|
| PASSED | 校验通过，数据正常 |
| FAILED | 发现异常，需关注 |
| SKIPPED | 数据不足或第三方不可用，跳过 |

示例输出：
```
OHLC: CN/000001.SZ          PASSED  all 30 bars OK
PriceChange: HK/00700.HK     PASSED  no anomaly in 60 bars (threshold ±50%)
Volume: US/AAPL              PASSED  volume normal across 60 bars
Freshness: CN/600000.SH      PASSED  latest=20260407, 1 day(s) ago
CrossVerify: CN/000001.SZ    PASSED  1 anomaly(s) all confirmed as real market data via 3rd party
```

---

## 六、配置调优

如需调整阈值，修改 `tests/v2/07_kline_quality/test_kline_quality.py` 顶部的常量：

```python
PRICE_CHANGE_THRESHOLD = {"cn": 30.0, "hk": 50.0, "us": 40.0}
VOLUME_SPIKE_MULTIPLIER = 15
FRESHNESS_MAX_DAYS = 2
```
