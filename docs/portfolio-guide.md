# 📊 模拟盘功能使用指南

> ⚠️ **免责声明**：本功能仅供模拟盘参考，不构成任何投资建议。股市有风险，投资需谨慎。

## 功能概述

模拟盘功能允许你：

1. **配置虚拟持仓** - 设置初始资金、持仓股票、成本价等
2. **自动计算收益** - 实时计算盈亏、收益率、仓位比例
3. **AI 操作建议** - 结合持仓和分析结果，生成加仓/减仓/止盈止损建议
4. **本地报告保存** - 将分析报告保存为 Markdown 文件，无需发送邮件

---

## 快速开始

### 1. 启用模拟盘功能

在 `.env` 文件中添加以下配置：

```bash
# 模拟盘配置
PORTFOLIO_ENABLED=true                    # 启用模拟盘
PORTFOLIO_CONFIG_PATH=./data/portfolio.json  # 仓位配置文件路径
GENERATE_OPERATION_ADVICE=true            # 生成 AI 操作建议

# 本地报告保存
SAVE_LOCAL_REPORT=true                    # 保存本地 MD 报告
REPORTS_DIR=./reports                     # 报告保存目录
```

### 2. 配置持仓信息

创建 `./data/portfolio.json` 文件（可参考 `docs/portfolio.example.json`）：

```json
{
  "initial_capital": 100000.0,
  "available_cash": 50000.0,
  "max_single_position_pct": 30.0,
  "stop_loss_pct": 8.0,
  "take_profit_pct": 20.0,
  "max_total_position_pct": 80.0,
  "positions": {
    "600519": {
      "code": "600519",
      "name": "贵州茅台",
      "shares": 100,
      "cost_price": 1800.0,
      "current_price": 1850.0,
      "buy_date": "2026-01-15",
      "notes": "白酒龙头"
    }
  }
}
```

### 3. 运行分析

```bash
python main.py --stocks 600519,300750
```

分析完成后：
- 报告自动保存到 `./reports/daily_2026-02-02.md`
- 控制台输出持仓摘要和风险预警
- AI 生成今日操作建议

---

## 配置项详解

### 账户配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `initial_capital` | 初始资金（元） | 100000 |
| `available_cash` | 可用现金（元） | 100000 |

### 风控参数

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `stop_loss_pct` | 止损线（%） | 8.0 |
| `take_profit_pct` | 止盈线（%） | 20.0 |
| `max_single_position_pct` | 单股最大仓位（%） | 30.0 |
| `max_total_position_pct` | 最大总仓位（%） | 80.0 |

### 交易费用

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `commission_rate` | 佣金费率 | 0.0003（万三） |
| `stamp_duty_rate` | 印花税率 | 0.001（千一） |
| `min_commission` | 最低佣金（元） | 5.0 |

### 持仓信息

每只股票的持仓信息包括：

| 字段 | 说明 | 必填 |
|------|------|:----:|
| `code` | 股票代码 | ✅ |
| `name` | 股票名称 | ✅ |
| `shares` | 持仓股数 | ✅ |
| `cost_price` | 成本价（买入均价） | ✅ |
| `current_price` | 当前价格 | 可选 |
| `buy_date` | 买入日期 | 可选 |
| `notes` | 备注 | 可选 |

---

## 环境变量配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `PORTFOLIO_ENABLED` | 是否启用模拟盘 | `true` |
| `PORTFOLIO_CONFIG_PATH` | 仓位配置文件路径 | `./data/portfolio.json` |
| `GENERATE_OPERATION_ADVICE` | 是否生成 AI 操作建议 | `true` |
| `SAVE_LOCAL_REPORT` | 是否保存本地报告 | `true` |
| `REPORTS_DIR` | 报告保存目录 | `./reports` |

---

## 报告输出

### 本地 Markdown 报告

每次运行后，报告自动保存到 `./reports/` 目录：

```
reports/
├── daily_2026-02-01.md    # 每日汇总（覆盖）
├── daily_2026-02-02.md
├── analysis_2026-02-02_180000.md  # 带时间戳的详细报告
└── ...
```

### 报告内容

1. **免责声明** - 模拟盘风险提示
2. **持仓报告** - 账户概览、持仓明细、风控参数
3. **风险预警** - 止损/止盈预警
4. **AI 操作建议** - 今日操作建议（加仓/减仓/调仓）
5. **大盘复盘** - 市场概况
6. **个股分析** - 详细分析结果

---

## AI 操作建议

启用 `GENERATE_OPERATION_ADVICE=true` 后，系统会：

1. 整合当前持仓信息
2. 结合个股分析结果
3. 检查风险预警（止损/止盈）
4. 调用 AI 生成操作建议

### 建议内容包括

- **整体仓位建议** - 是否需要调整总仓位
- **个股操作建议** - 加仓/减仓/止盈/止损
- **具体操作计划** - 建议数量、目标价位
- **风险提示** - 当前需要注意的风险点

---

## 风险预警

系统会自动检查以下风险：

| 预警类型 | 触发条件 | 建议操作 |
|----------|----------|----------|
| 🔴 止损预警 | 亏损 ≥ 止损线 | 建议止损卖出 |
| ⚡ 止损接近 | 亏损 ≥ 止损线×70% | 密切关注 |
| 🎉 止盈达标 | 盈利 ≥ 止盈线 | 建议分批止盈 |
| 📈 止盈接近 | 盈利 ≥ 止盈线×80% | 考虑部分止盈 |
| ⚠️ 仓位超限 | 总仓位 ≥ 最大仓位 | 不建议加仓 |

---

## 使用示例

### 示例 1：基本使用

```bash
# 配置 .env
PORTFOLIO_ENABLED=true
SAVE_LOCAL_REPORT=true
STOCK_LIST=600519,300750,002594

# 运行
python main.py
```

### 示例 2：仅保存本地报告，不发送通知

```bash
python main.py --no-notify
```

### 示例 3：调试模式

```bash
python main.py --debug
```

---

## 常见问题

### Q: 如何修改持仓？

直接编辑 `./data/portfolio.json` 文件，下次运行时自动生效。

### Q: 报告保存在哪里？

默认保存在 `./reports/` 目录，可通过 `REPORTS_DIR` 环境变量修改。

### Q: 如何禁用 AI 操作建议？

设置 `GENERATE_OPERATION_ADVICE=false`。

### Q: 持仓价格如何更新？

系统会在分析时自动从行情数据更新持仓价格。

---

## 免责声明

⚠️ **重要提示**

- 本功能仅供模拟盘参考，不构成任何投资建议
- 所有分析结果仅基于历史数据和 AI 模型推断
- 股市有风险，投资需谨慎
- 作者不对使用本系统产生的任何损失负责
- 请在做出投资决策前咨询专业投资顾问
