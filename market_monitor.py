#!/usr/bin/env python3
"""
A股涨停情绪监控
每日收盘后统计涨停、炸板、连板等数据，输出Excel
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import os


def get_zt_data(date: str = None) -> pd.DataFrame:
    """获取涨停数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_em(date=date)
        return df
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return pd.DataFrame()


def get_zb_data(date: str = None) -> pd.DataFrame:
    """获取炸板数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date)
        return df
    except Exception as e:
        print(f"获取炸板数据失败: {e}")
        return pd.DataFrame()


def get_dt_data(date: str = None) -> pd.DataFrame:
    """获取跌停数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date)
        return df
    except Exception as e:
        print(f"获取跌停数据失败: {e}")
        return pd.DataFrame()


def get_zt_pool_strong(date: str = None) -> pd.DataFrame:
    """获取强势股数据（曾涨停）"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_strong_em(date=date)
        return df
    except Exception as e:
        print(f"获取强势股数据失败: {e}")
        return pd.DataFrame()


def get_previous_zt_return(date: str = None) -> dict:
    """计算昨日涨停今日收益"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    # 获取昨日日期
    from datetime import timedelta
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    
    try:
        # 昨日涨停股
        prev_zt = ak.stock_zt_pool_em(date=yesterday)
        if prev_zt.empty:
            return {"昨日涨停溢价": None, "昨板今均": None}
        
        # 获取今日行情
        today_spot = ak.stock_zh_a_spot_em()
        
        # 计算昨日涨停股今日平均涨幅
        codes = prev_zt["代码"].tolist()
        matched = today_spot[today_spot["代码"].isin(codes)]
        
        if matched.empty:
            return {"昨日涨停溢价": None, "昨板今均": None}
        
        avg_return = matched["涨跌幅"].mean()
        return {"昨日涨停溢价": f"{avg_return:.2f}%", "昨板今均": f"{avg_return:.2f}%"}
    except Exception as e:
        print(f"计算昨日涨停收益失败: {e}")
        return {"昨日涨停溢价": None, "昨板今均": None}


def calculate_market_stats(date: str = None) -> dict:
    """计算市场情绪指标"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"正在统计 {date} 的市场数据...")
    
    # 获取各类数据
    zt_df = get_zt_data(date)
    zb_df = get_zb_data(date)
    dt_df = get_dt_data(date)
    strong_df = get_zt_pool_strong(date)
    
    # 基础统计
    zt_count = len(zt_df)
    zb_count = len(zb_df)
    dt_count = len(dt_df)
    strong_count = len(strong_df)
    
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
    lb_ge_2 = sum(1 for lb in lb_counts.keys() if lb >= 2) if lb_counts else 0
    
    # 高度板
    height_board = max_lb
    
    # 涨跌停比
    zt_dt_ratio = zt_count / dt_count if dt_count > 0 else float('inf')
    
    # 获取昨日涨停收益
    prev_return = get_previous_zt_return(date)
    
    # 跌幅>5%的股票数
    try:
        spot_df = ak.stock_zh_a_spot_em()
        drop_5pct = len(spot_df[spot_df["涨跌幅"] <= -5])
        total_stocks = len(spot_df)
        up_down_ratio = len(spot_df[spot_df["涨跌幅"] > 0]) / len(spot_df[spot_df["涨跌幅"] < 0]) if len(spot_df[spot_df["涨跌幅"] < 0]) > 0 else float('inf')
    except:
        drop_5pct = None
        up_down_ratio = None
        total_stocks = None
    
    stats = {
        "日期": date,
        "总体涨跌比": f"{up_down_ratio:.2f}" if up_down_ratio and up_down_ratio != float('inf') else "N/A",
        "涨停": zt_count,
        "跌停": dt_count,
        "曾涨停": strong_count,
        "炸板": zb_count,
        "炸板率": f"{zb_rate:.2f}%",
        "连板个数": lb_ge_2,
        "高度板": int(height_board) if height_board else 0,
        "昨日涨停红盘比例": prev_return.get("昨日涨停溢价", "N/A"),
        "昨板今均": prev_return.get("昨板今均", "N/A"),
        "跌幅-5%以上": drop_5pct if drop_5pct else "N/A",
    }
    
    return stats


def save_to_excel(stats: dict, date: str = None):
    """保存统计结果到Excel"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    # 创建DataFrame
    df = pd.DataFrame([stats])
    
    # 调整列顺序
    columns_order = [
        "日期", "总体涨跌比", "昨日涨停红盘比例", "昨板今均", 
        "连板个数", "涨停", "曾涨停", "炸板率", "跌停", 
        "跌幅-5%以上", "高度板"
    ]
    df = df[[col for col in columns_order if col in df.columns]]
    
    # 文件名
    filename = f"market_stats_{date}.xlsx"
    
    # 保存
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"数据已保存到: {filename}")
    return filename


def main():
    """主函数"""
    date = datetime.now().strftime("%Y%m%d")
    print(f"=== A股涨停情绪监控 {date} ===\n")
    
    # 计算统计
    stats = calculate_market_stats(date)
    
    # 打印结果
    print("\n=== 统计结果 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 保存到Excel
    filename = save_to_excel(stats, date)
    print(f"\n完成！文件: {filename}")


if __name__ == "__main__":
    main()
