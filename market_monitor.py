#!/usr/bin/env python3
"""
A股涨停情绪监控 - 东方财富数据源
每日收盘后统计涨停、炸板、连板等数据，输出Excel
"""

import pandas as pd
from datetime import datetime, timedelta
from kaipanla_api import get_em_zt_pool, get_em_zb_pool, get_em_dt_pool, get_em_yesterday_zt_return


def calculate_market_stats(date: str = None) -> dict:
    """计算市场情绪指标（东方财富数据源）"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"正在从东方财富获取 {date} 的市场数据...")
    
    # 获取各类数据
    zt_df = get_em_zt_pool(date)
    zb_df = get_em_zb_pool(date)
    dt_df = get_em_dt_pool(date)
    
    # 基础统计
    zt_count = len(zt_df)
    zb_count = len(zb_df)
    dt_count = len(dt_df)
    
    # 曾涨停 = 涨停 + 炸板
    strong_count = zt_count + zb_count
    
    # 炸板率
    total_zt_attempt = zt_count + zb_count
    zb_rate = (zb_count / total_zt_attempt * 100) if total_zt_attempt > 0 else 0
    
    # 连板统计
    lb_counts = {}
    max_lb = 0
    if not zt_df.empty and "连板数" in zt_df.columns:
        lb_series = pd.to_numeric(zt_df["连板数"], errors='coerce').fillna(0)
        lb_counts = lb_series.value_counts().to_dict()
        max_lb = int(lb_series.max()) if not lb_series.empty else 0
    
    # 连板个数（2板及以上）
    lb_ge_2 = sum(count for lb, count in lb_counts.items() if lb >= 2) if lb_counts else 0
    
    # 高度板
    height_board = max_lb
    
    # 计算昨日涨停溢价
    prev_return = get_em_yesterday_zt_return(date)
    
    stats = {
        "日期": date,
        "涨停": zt_count,
        "炸板": zb_count,
        "跌停": dt_count,
        "曾涨停": strong_count,
        "炸板率": f"{zb_rate:.2f}%",
        "连板个数": lb_ge_2,
        "高度板": height_board,
        "昨日涨停红盘比例": prev_return.get("红盘比例", "N/A"),
        "昨板今均": prev_return.get("平均涨幅", "N/A"),
    }
    
    # 打印详细连板分布
    if lb_counts:
        print("\n连板分布:")
        for lb in sorted(lb_counts.keys(), reverse=True):
            if lb > 0:
                print(f"  {int(lb)}板: {lb_counts[lb]} 只")
    
    return stats, zt_df, zb_df


def save_to_excel(stats: dict, date: str = None, zt_df: pd.DataFrame = None, zb_df: pd.DataFrame = None):
    """保存统计结果到Excel，包含详细股票列表"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    filename = f"market_stats_{date}.xlsx"
    
    # 创建Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: 汇总统计
        summary_df = pd.DataFrame([stats])
        summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
        
        # Sheet 2: 涨停明细
        if zt_df is not None and not zt_df.empty:
            zt_df.to_excel(writer, sheet_name='涨停明细', index=False)
        
        # Sheet 3: 炸板明细
        if zb_df is not None and not zb_df.empty:
            zb_df.to_excel(writer, sheet_name='炸板明细', index=False)
    
    print(f"\n数据已保存到: {filename}")
    return filename


def main():
    """主函数"""
    date = datetime.now().strftime("%Y%m%d")
    print(f"=== A股涨停情绪监控（东方财富数据源）{date} ===\n")
    
    # 获取涨停和炸板数据（用于保存明细）
    zt_df = get_em_zt_pool(date)
    zb_df = get_em_zb_pool(date)
    
    # 计算统计
    stats, zt_df, zb_df = calculate_market_stats(date)
    
    # 打印结果
    print("\n=== 统计结果 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 保存到Excel
    filename = save_to_excel(stats, date, zt_df, zb_df)
    print(f"\n完成！文件: {filename}")


if __name__ == "__main__":
    main()