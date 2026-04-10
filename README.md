# Market Data Service Test

market-data-service 接口自动化测试框架。

## 环境准备

```bash
cd market-data-service-test
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 配置

服务地址和 API Key 通过环境变量配置（默认值见 `config.py`）：

| 环境变量 | 说明 | 默认值 |
|---------|------|-------|
| `MARKET_DATA_SERVICE_URL` | 服务地址 | `http://172.17.0.1:3101` |
| `MARKET_DATA_API_KEY` | API Key | 见 `config.py` |
| `VERBOSE` | 详细日志 | `true` |
| `REPORT_DIR` | 报告输出目录 | `./reports` |

示例：测试其他环境的服务

```bash
export MARKET_DATA_SERVICE_URL=http://192.168.1.100:3101
python scripts/run_v2.py -m hkstock
```

## 运行测试

### 快速冒烟测试（几秒）

```bash
python scripts/run_quick.py
```

### 运行全部 V2 测试

```bash
python scripts/run_v2.py
```

### 按模块运行

`-m` 指定模块，可选值：`common`、`indicators`、`crypto`、`cnstock`、`hkstock`、`usstock`、`market`、`kline_quality`

```bash
# 只测港股
python scripts/run_v2.py -m hkstock

# 只测美股
python scripts/run_v2.py -m usstock

# 港股 + 美股
python scripts/run_v2.py -m hkstock -m usstock

# 统一行情接口（HK/CN/US）
python scripts/run_v2.py -m market

# K线数据质量校验
python scripts/run_v2.py -m kline_quality
```

### 港股指标测试

测试港股 26 个技术指标（SMA、EMA、RSI、MACD、BOLL、KDJ、ATR、OBV、CCI、ADX、VWAP 等），使用 00700.HK 和 00941.HK：

```bash
python scripts/run_v2.py -m hkstock
```

### 美股指标测试

测试美股 26 个技术指标（SMA、EMA、RSI、MACD、BOLL、KDJ、ATR、OBV、CCI、ADX、VWAP 等），使用 AAPL、MSFT、GOOGL：

```bash
python scripts/run_v2.py -m usstock
```

### 加密货币指标测试

测试 26 个技术指标（SMA、EMA、RSI、MACD、BOLL、KDJ、ADX 等）：

```bash
python scripts/run_v2.py -m indicators
```

### K线数据质量校验

校验 A股/港股/美股 K线数据质量（OHLC 完整性、价格异常、成交量异常、数据新鲜度、第三方交叉验证）：

```bash
python scripts/run_v2.py -m kline_quality
```

### A股测试

```bash
python scripts/run_v2.py -m cnstock
```

### 运行全部测试（含 V1 历史接口）

```bash
python scripts/run_all.py
python scripts/run_all.py --include-v1
```

### CI 模式（静默输出）

```bash
python scripts/run_ci.py
```

## 测试报告

测试完成后自动生成报告到 `reports/` 目录，包含 JSON 和 HTML 两种格式。

## 项目结构

```
market-data-service-test/
├── config.py                  # 配置（服务地址、API Key、测试参数）
├── framework/                 # 测试框架
│   ├── base.py                # BaseTester、TestResult
│   └── api_client.py          # API 客户端（V1/V2 全部接口封装）
├── scripts/
│   ├── run_v2.py              # V2 测试入口（按模块运行）
│   ├── run_all.py             # 全部测试
│   ├── run_quick.py           # 快速冒烟测试
│   └── run_ci.py              # CI 模式
├── tests/
│   ├── common/                # 健康检查
│   └── v2/
│       ├── 01_crypto/         # 加密货币（K线、资金费率、爆仓、持仓等）
│       ├── 02_indicators/     # 通用指标（26 个技术指标）
│       ├── 03_cnstock/        # A股（行情、财务、资金流、宏观数据等）
│       ├── 04_hkstock/        # 港股（行情、港股通、指标计算）
│       ├── 05_usstock/        # 美股（行情、指标计算）
│       ├── 06_market/         # 统一行情接口（实时报价、Fuxin 分时/五档/十档/逐笔）
│       └── 07_kline_quality/  # K线数据质量校验（OHLC/价格异常/成交量/新鲜度）
├── docs/                      # 项目文档
└── reports/                   # 测试报告输出
```
