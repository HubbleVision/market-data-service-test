# 复星行情接口自测方案

> 创建时间: 2026-04-08
> 关联: 1-fuxin分时数据.md、2-fuxin其他接口.md

---

## 一、自测背景

复星（Fosun）行情接口已实现以下功能：
- 分时数据（min）— 3个市场路由
- 五档买卖盘（brokerq）— 3个市场路由
- 十档买卖盘（orderbook）— 3个市场路由
- 逐笔成交（tick）— 3个市场路由
- 实时报价（securities/quote）— 已有测试，不在本次范围

共 **12 个端点**，本次覆盖 min/brokerq/orderbook/tick 共 **12 个端点**。

---

## 二、接口清单与响应结构

> **响应结构差异**: `brokerq`/`orderbook`/`tick` 响应包含 `body` 包装层（`{"body": {"success": true, ...}}`），`min` 响应直接返回 `{"success": true, ...}`。测试代码中通过 `_get_body()` 辅助函数统一处理两种情况。

### 2.1 分时数据 (min)

**端点**: `GET /api/v2/{cnstock|hkstock|usstock}/min?code={code}&ktype={ktype}`

**参数说明**:

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `code` | 是 | string | 证券代码，支持多种格式（见下方代码格式说明） |
| `ktype` | 否 | string | K线类型：`min1`（1分钟，默认）、`min5`（5分钟） |

**响应结构**（直接返回，无 body 包装层）:
```json
{
  "success": true,
  "symbol": "600519",
  "pClose": 1675.30,
  "data": [
    {
      "time": 1744064400,
      "timeStr": "09:30",
      "price": 1680.50,
      "avg": 1682.30,
      "volume": 5000,
      "turnover": 8402500,
      "chgVal": 5.20,
      "chgPct": 0.31
    }
  ],
  "timestamp": 1744064400000
}
```

**空数据时**: `success: true, data: [], message: "无分时数据（可能非交易时段）"`

### 2.2 五档买卖盘 (brokerq)

**端点**: `GET /api/v2/{cnstock|hkstock|usstock}/brokerq?code={code}`

**参数说明**:

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `code` | 是 | string | 证券代码，支持多种格式 |

**响应结构**（带 body 包装层）:
```json
{
  "body": {
    "success": true,
    "symbol": "600519",
    "bid": [
      {"price": 1680.50, "vol": 500, "orderCount": 10}
    ],
    "ask": [
      {"price": 1680.60, "vol": 600, "orderCount": 12}
    ]
  }
}
```

**字段说明**: `bid`/`ask` 各最多 5 档。`bid` 价格降序排列，`ask` 价格升序排列。`orderCount` 为该档位的委托订单数。

**空数据时**: `success: true, bid: [], ask: [], message: "无五档数据（可能非交易时段或停牌）"`

### 2.3 十档买卖盘 (orderbook)

**端点**: `GET /api/v2/{cnstock|hkstock|usstock}/orderbook?code={code}`

**参数说明**:

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `code` | 是 | string | 证券代码，支持多种格式 |

**响应结构**（带 body 包装层）:
```json
{
  "body": {
    "success": true,
    "symbol": "600519",
    "bid": [{"price": 1680.50, "vol": 500}],
    "ask": [{"price": 1680.60, "vol": 600}]
  }
}
```

**字段说明**: `bid`/`ask` 各最多 10 档。`bid` 价格降序排列，`ask` 价格升序排列。

### 2.4 逐笔成交 (tick)

**端点**: `GET /api/v2/{cnstock|hkstock|usstock}/tick?code={code}&lastTime={lastTime}&count={count}`

**参数说明**:

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `code` | 是 | string | 证券代码，支持多种格式 |
| `lastTime` | 否 | string | 增量拉取游标，值为上次响应中返回的 `lastTime` 字段 |
| `count` | 否 | int | 限制返回条数（如 `count=5` 最多返回 5 条） |

**响应结构**（带 body 包装层）:
```json
{
  "body": {
    "success": true,
    "symbol": "600519",
    "lastTime": "20260408093125003",
    "ticks": [
      {"time": 1744064215000, "timeStr": "09:30:15.000", "price": 1680.50, "vol": 100, "turnover": 168050, "direction": 1}
    ]
  }
}
```

**字段说明**: `direction` 成交方向，取值：`0`（中性）、`1`（买盘）、`2`（卖盘）。`lastTime` 用于增量拉取，传入该值可获取该时间点之后的新成交数据。

### 2.5 证券代码格式说明

CN 市场支持多种代码格式输入，服务端会自动规范化：

| 输入格式 | 示例 | 解析结果 |
|---------|------|---------|
| 纯代码 | `600519` | 600519 |
| 带交易所前缀 | `sh600519` / `sz000001` | 600519 / 000001（自动识别 sh/sz/bj） |
| 带后缀 | `600519.SH` / `000001.SZ` | 600519 / 000001（去除 `.XX` 后缀） |

HK/US 市场直接使用纯代码（如 `00700`、`AAPL`）。

---

## 三、测试策略

### 测试范围

| 维度 | 覆盖内容 |
|------|---------|
| 三市场 | A股（sh/sz/bj）、港股、美股 各至少一只标的 |
| 正常流程 | 有数据返回时，验证响应结构和字段类型 |
| 空数据 | 非交易时段，验证 success=true + 空 data + message |
| 代码格式 | 纯代码 / 带前缀 / 带后缀 三种格式 |
| 代码前缀推断 | cn 市场下 sh/sz/bj 自动判断 |
| 响应时间 | 所有请求应在 5s 内返回 |
| ktype 参数 | min 接口支持 min1/min5 两种类型 |
| 增量拉取 | tick 接口 lastTime 参数增量获取新数据 |
| 条数限制 | tick 接口 count 参数限制返回条数 |

### 测试标的

| 市场 | 代码 | 交易所 | 说明 |
|------|------|--------|------|
| CN (sh) | 600519 | 上交所 | 贵州茅台，高流动性 |
| CN (sz) | 000001 | 深交所 | 平安银行，高流动性 |
| HK | 00700 | 港交所 | 腾讯控股 |
| US | AAPL | 纳斯达克 | 苹果公司 |

### 不测试的内容

- securities/quote 接口（已有测试 `test_market_quote.py`）
- 极端并发、压力测试
- 鉴权错误（统一中间件处理）

---

## 四、测试用例设计

### 4.1 分时数据 (test_fuxin_min.py)

| # | 用例 | 验证点 |
|---|------|--------|
| 1 | CN 分时 - 茅台 (600519) | success=true, symbol, pClose>0, data 数组, time/timeStr/price 等字段类型 |
| 2 | CN 分时 - 平安银行 (000001) | sh/sz 自动推断 (sz), 响应结构完整 |
| 3 | HK 分时 - 腾讯 (00700) | 港股响应结构完整 |
| 4 | US 分时 - AAPL | 美股响应结构完整 |
| 5 | CN 分时 - 带前缀 (sh600519) | stripMarketPrefix 正常处理，symbol=600519 |
| 6 | CN 分时 - 带后缀 (600519.SH) | stripMarketPrefix 正常处理，symbol=600519 |
| 7 | CN 分时 - ktype=min5 | ktype 参数正常工作，返回 5 分钟级别数据 |
| 8 | 响应结构校验 | success/symbol/pClose/timestamp 字段存在且类型正确 |
| 9 | 空数据/非交易时段 | data=[], message 不为空 |

### 4.2 五档买卖盘 (test_fuxin_brokerq.py)

| # | 用例 | 验证点 |
|---|------|--------|
| 1 | CN 五档 - 茅台 | success=true, bid/ask 各 5 档, price/vol/orderCount |
| 2 | CN 五档 - 平安银行 | sz 交易所自动推断 |
| 3 | HK 五档 - 腾讯 | 港股响应 |
| 4 | US 五档 - AAPL | 美股响应 |
| 5 | 档位排序 | bid 降序, ask 升序 |
| 6 | 带前缀/后缀格式 | stripMarketPrefix 兼容 |
| 7 | 空数据 | success=true, bid=[], ask=[], message |

### 4.3 十档买卖盘 (test_fuxin_orderbook.py)

| # | 用例 | 验证点 |
|---|------|--------|
| 1 | CN 十档 - 茅台 | success=true, bid/ask 各 10 档, price/vol |
| 2 | CN 十档 - 平安银行 | sz 交易所 |
| 3 | HK 十档 - 腾讯 | 港股响应 |
| 4 | US 十档 - AAPL | 美股响应 |
| 5 | 档位排序 | bid 降序, ask 升序 |
| 6 | 带前缀/后缀格式 | stripMarketPrefix 兼容 |
| 7 | 空数据 | success=true, bid=[], ask=[], message |

### 4.4 逐笔成交 (test_fuxin_tick.py)

| # | 用例 | 验证点 |
|---|------|--------|
| 1 | CN 逐笔 - 茅台 | success=true, ticks 数组, lastTime, time/timeStr/price/vol/turnover/direction |
| 2 | CN 逐笔 - 平安银行 | sz 交易所 |
| 3 | HK 逐笔 - 腾讯 | 港股响应 |
| 4 | US 逐笔 - AAPL | 美股响应 |
| 5 | direction 取值 | 所有 tick 的 direction 均为 0/1/2 有效值 |
| 6 | lastTime 增量拉取 | 使用首次请求返回的 lastTime 传入二次请求，验证增量数据返回 |
| 7 | count 参数 | count=5 时返回条数不超过 5 |
| 8 | 带前缀/后缀格式 | stripMarketPrefix 兼容 |
| 9 | 空数据 | success=true, ticks=[], message |

---

## 五、涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `framework/api_client.py` | 改 | 新增 4 个 client 方法 (min/brokerq/orderbook/tick) |
| `tests/v2/06_market/test_fuxin_min.py` | 新建 | 分时数据自测 |
| `tests/v2/06_market/test_fuxin_brokerq.py` | 新建 | 五档买卖盘自测 |
| `tests/v2/06_market/test_fuxin_orderbook.py` | 新建 | 十档买卖盘自测 |
| `tests/v2/06_market/test_fuxin_tick.py` | 新建 | 逐笔成交自测 |
| `scripts/run_v2.py` | 改 | market 模块注册新测试 |

---

## 六、注意事项

1. **非交易时段**: 所有接口在非交易时段可能返回空数据，测试用例应兼容空数据场景（标记 SKIP 而非 FAIL）
2. **brokerq/orderbook 响应外层差异**: brokerq/orderbook/tick 响应包含 `body` 包装层（`{"body": {"success": true, ...}}`），min 响应直接返回 `{"success": true, ...}`。测试代码通过 `_get_body()` 辅助函数统一处理：优先检查 `data["body"]`，不存在时直接使用 `data`
3. **price 转换**: 价格已由 SDK 层转换（除以 power），测试时验证 price > 0 即可
4. **响应时间**: SDK 配置 15s 超时 + 3 次重试，测试端 30s 超时足够
5. **tick 增量拉取**: `lastTime` 为游标值（如 `20260408093125003`），非时间戳格式。首次请求获取 lastTime，后续请求传入即可获取增量数据
6. **tick count 限制**: `count` 参数限制返回条数，不传则返回全部可用数据
7. **min ktype 参数**: `ktype` 支持 `min1`（默认）和 `min5`，不传时默认 1 分钟级别
