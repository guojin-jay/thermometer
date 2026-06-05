#!/usr/bin/env python3
"""
A股涨停情绪监控 - 开盘啦数据源
每日收盘后统计涨停、炸板、连板等数据，输出Excel
"""

import pandas as pd
from datetime import datetime, timedelta
import os
from kaipanla_api import get_kaipanla_zt, get_kaipanla_zb, get_kaipanla_dt


def calculate_market_stats(date: str = None) -> dict:
    """计算市场情绪指标（开盘啦数据源）"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"正在从开盘啦获取 {date} 的市场数据...")
    
    # 获取各类数据
    zt_df = get_kaipanla_zt(date)
    zb_df = get_kaipanla_zb(date)
    dt_df = get_kaipanla_dt(date)
    
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
        lb_counts = zt_df["连板数"].value_counts().to_dict()
        max_lb = zt_df["连板数"].max() if not zt_df["连板数"].empty else 0
    
    # 连板个数（2板及以上）
    lb_ge_2 = sum(count for lb, count in lb_counts.items() if lb >= 2) if lb_counts else 0
    
    # 高度板
    height_board = int(max_lb) if max_lb else 0
    
    # 计算昨日涨停溢价
    prev_return = calculate_prev_zt_return(date)
    
    # 涨跌停比
    zt_dt_ratio = zt_count / dt_count if dt_count > 0 else float('inf')
    
    stats = {
        "日期": date,
        "总体涨跌比": "需补充",  # 开盘啦需要额外接口
        "涨停": zt_count,
        "跌停": dt_count,
        "曾涨停": strong_count,
        "炸板": zb_count,
        "炸板率": f"{zb_rate:.2f}%",
        "连板个数": lb_ge_2,
        "高度板": height_board,
        "昨日涨停红盘比例": prev_return.get("红盘比例", "N/A"),
        "昨板今均": prev_return.get("平均涨幅", "N/A"),
        "跌幅-5%以上": "需补充",  # 需要额外计算
    }
    
    # 打印详细连板分布
    if lb_counts:
        print("\n连板分布:")
        for lb in sorted(lb_counts.keys(), reverse=True):
            print(f"  {lb}板: {lb_counts[lb]} 只")
    
    return stats


def calculate_prev_zt_return(date: str = None) -> dict:
    """计算昨日涨停股今日表现"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"\n计算昨日 ({yesterday}) 涨停股今日表现...")
    
    # 获取昨日涨停股
    prev_zt_df = get_kaipanla_zt(yesterday)
    
    if prev_zt_df.empty:
        print("昨日无涨停数据")
        return {"红盘比例": "N/A", "平均涨幅": "N/A"}
    
    prev_codes = set(prev_zt_df["代码"].tolist())
    print(f"昨日涨停股数量: {len(prev_codes)}")
    
    # 获取今日涨停数据（包含涨跌幅信息）
    today_zt_df = get_kaipanla_zt(date)
    
    # 获取今日炸板数据
    today_zb_df = get_kaipanla_zb(date)
    
    # 合并今日数据
    today_data = {}
    
    # 从涨停数据获取
    if not today_zt_df.empty:
        for _, row in today_zt_df.iterrows():
            code = row.get("代码")
            if code:
                # 涨停股今日涨幅设为10%（或实际涨停幅度）
                today_data[code] = 10.0
    
    # 从炸板数据获取实际涨跌幅
    if not today_zb_df.empty:
        for _, row in today_zb_df.iterrows():
            code = row.get("代码")
            zdf = row.get("涨跌幅")
            if code and zdf is not None:
                today_data[code] = float(zdf)
    
    # 计算昨日涨停股今日表现
    returns = []
    red_count = 0
    
    for code in prev_codes:
        if code in today_data:
            ret = today_data[code]
            returns.append(ret)
            if ret > 0:
                red_count += 1
    
    if not returns:
        return {"红盘比例": "N/A", "平均涨幅": "N/A"}
    
    avg_return = sum(returns) / len(returns)
    red_ratio = red_count / len(prev_codes) * 100
    
    return {
        "红盘比例": f"{red_ratio:.1f}%",
        "平均涨幅": f"{avg_return:.2f}%"
    }


def save_to_excel(stats: dict, date: str = None, zt_df: pd.DataFrame = None):
    """保存统计结果到Excel，包含详细股票列表"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    filename = f"market_stats_{date}.xlsx"
    
    # 创建Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: 汇总统计
        summary_df = pd.DataFrame([stats])
        columns_order = [
            "日期", "总体涨跌比", "昨日涨停红盘比例", "昨板今均", 
            "连板个数", "涨停", "曾涨停", "炸板率", "跌停", 
            "跌幅-5%以上", "高度板"
        ]
        summary_df = summary_df[[col for col in columns_order if col in summary_df.columns]]
        summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
        
        # Sheet 2: 涨停明细
        if zt_df is not None and not zt_df.empty:
            zt_df.to_excel(writer, sheet_name='涨停明细', index=False)
    
    print(f"\n数据已保存到: {filename}")
    return filename


def main():
    """主函数"""
    date = datetime.now().strftime("%Y%m%d")
    print(f"=== A股涨停情绪监控（开盘啦数据源）{date} ===\n")
    
    # 获取涨停数据（用于保存明细）
    zt_df = get_kaipanla_zt(date)
    
    # 计算统计
    stats = calculate_market_stats(date)
    
    # 打印结果
    print("\n=== 统计结果 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 保存到Excel
    filename = save_to_excel(stats, date, zt_df)
    print(f"\n完成！文件: {filename}")


if __name__ == "__main__":
    main()
