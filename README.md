# 温度计 - A股涨停情绪监控

每日收盘后自动统计A股涨停、炸板、连板等市场情绪指标。

## 数据源

**开盘啦** (https://www.kaipanla.com)

## 功能

- 📊 涨停家数、跌停家数统计
- 💥 炸板率计算
- 🔗 连板股个数、高度板追踪
- 📈 昨日涨停今日溢价
- 📋 输出Excel报表（含涨停明细）

## 文件说明

| 文件 | 说明 |
|------|------|
| market_monitor.py | 主程序，统计并生成Excel |
| kaipanla_api.py | 开盘啦数据接口 |
| equirements.txt | Python依赖包 |

## 安装依赖

`ash
pip install -r requirements.txt
`

## 使用

`ash
python market_monitor.py
`

运行后生成 market_stats_YYYYMMDD.xlsx 文件，包含：
- **汇总统计** Sheet：各项指标汇总
- **涨停明细** Sheet：当日所有涨停股票详情

## 定时运行

GitHub Actions 已配置，每日收盘后自动执行（需确保开盘啦API可用）。