#!/usr/bin/env python3
"""
A股涨停情绪监控 - AKShare 数据源
每日收盘后统计涨停、炸板、连板等数据，输出Excel
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def get_zt_pool(date: str = None) -> pd.DataFrame:
    """获取涨停池数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_em(date=date)
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return pd.DataFrame()


def get_zb_pool(date: str = None) -> pd.DataFrame:
    """获取炸板池数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date)
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        print(f"获取炸板数据失败: {e}")
        return pd.DataFrame()


def get_dt_pool(date: str = None) -> pd.DataFrame:
    """获取跌停池数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date)
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        print(f"获取跌停数据失败: {e}")
        return pd.DataFrame()


def get_market_spot() -> pd.DataFrame:
    """获取全市场实时行情"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        print(f"获取全市场数据失败: {e}")
        return pd.DataFrame()


def calculate_stats(date: str = None) -> dict:
    """计算市场情绪指标"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"正在获取 {date} 的市场数据...\n")
    
    # ========== 基础数据 ==========
    zt_df = get_zt_pool(date)
    zb_df = get_zb_pool(date)
    dt_df = get_dt_pool(date)
    spot_df = get_market_spot()
    
    # ========== 1. 总体涨跌比 ==========
    if not spot_df.empty and "涨跌幅" in spot_df.columns:
        up_count = len(spot_df[spot_df["涨跌幅"] > 0])
        down_count = len(spot_df[spot_df["涨跌幅"] < 0])
        total_up_down_ratio = up_count / down_count if down_count > 0 else float('inf')
        total_up_down_ratio_str = f"{total_up_down_ratio:.2f}"
        
        # 跌幅超5%
        drop_5pct_count = len(spot_df[spot_df["涨跌幅"] <= -5])
    else:
        total_up_down_ratio_str = "N/A"
        drop_5pct_count = "N/A"
    
    # ========== 2. 涨停炸板统计 ==========
    zt_count = len(zt_df)
    zb_count = len(zb_df)
    dt_count = len(dt_df)
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
    
    lb_ge_2 = sum(count for lb, count in lb_counts.items() if lb >= 2) if lb_counts else 0
    height_board = max_lb
    
    # 打印连板分布
    if lb_counts:
        print("连板分布:")
        for lb in sorted(lb_counts.keys(), reverse=True):
            if lb > 0:
                print(f"  {int(lb)}板: {lb_counts[lb]} 只")
    
    # ========== 3. 昨日涨停今日表现 ==========
    print(f"\n计算昨日 ({yesterday}) 涨停股今日表现...")
    prev_zt_df = get_zt_pool(yesterday)
    
    if prev_zt_df.empty:
        zt_red_ratio_str = "N/A"
        zt_avg_return_str = "N/A"
        lb_avg_return_str = "N/A"
    else:
        prev_codes = set(prev_zt_df["代码"].tolist())
        print(f"昨日涨停股数量: {len(prev_codes)}")
        
        # 获取今日涨停和炸板数据来计算昨日涨停股今日表现
        today_zt_df = get_zt_pool(date)
        today_zb_df = get_zb_pool(date)
        
        # 今日涨停股代码
        today_zt_codes = set(today_zt_df["代码"].tolist()) if not today_zt_df.empty else set()
        # 今日炸板股代码
        today_zb_codes = set(today_zb_df["代码"].tolist()) if not today_zb_df.empty else set()
        
        # 昨日涨停今日涨停的
        zt_zt_codes = prev_codes & today_zt_codes
        
        # 计算昨日涨停股今日平均涨幅
        # 需要获取这些股票今日的实际涨跌幅
        if not spot_df.empty:
            prev_zt_today = spot_df[spot_df["代码"].isin(prev_codes)]
            if not prev_zt_today.empty:
                avg_return = prev_zt_today["涨跌幅"].mean()
                red_count = len(prev_zt_today[prev_zt_today["涨跌幅"] > 0])
                zt_red_ratio = red_count / len(prev_codes) * 100
                zt_red_ratio_str = f"{zt_red_ratio:.1f}%"
                zt_avg_return_str = f"{avg_return:.2f}%"
            else:
                zt_red_ratio_str = "N/A"
                zt_avg_return_str = "N/A"
        else:
            zt_red_ratio_str = "N/A"
            zt_avg_return_str = "N/A"
        
        # ========== 4. 连板收益 ==========
        # 昨日连板股（连板数>=2）
        if "连板数" in prev_zt_df.columns:
            prev_lb_df = prev_zt_df[prev_zt_df["连板数"] >= 2]
            if not prev_lb_df.empty:
                prev_lb_codes = set(prev_lb_df["代码"].tolist())
                print(f"昨日连板股数量: {len(prev_lb_codes)}")
                
                if not spot_df.empty:
                    prev_lb_today = spot_df[spot_df["代码"].isin(prev_lb_codes)]
                    if not prev_lb_today.empty:
                        lb_avg_return = prev_lb_today["涨跌幅"].mean()
                        lb_avg_return_str = f"{lb_avg_return:.2f}%"
                    else:
                        lb_avg_return_str = "N/A"
                else:
                    lb_avg_return_str = "N/A"
            else:
                lb_avg_return_str = "N/A"
        else:
            lb_avg_return_str = "N/A"
    
    # ========== 汇总统计 ==========
    stats = {
        "日期": date,
        "总体涨跌比": total_up_down_ratio_str,
        "昨日涨停红盘比例": zt_red_ratio_str,
        "昨板今均": zt_avg_return_str,
        "做连板收益": lb_avg_return_str,
        "连板个数": lb_ge_2,
        "涨停": zt_count,
        "曾涨停": strong_count,
        "炸板率": f"{zb_rate:.2f}%",
        "跌停": dt_count,
        "跌幅-5%以上": drop_5pct_count,
        "高度板": height_board,
    }
    
    return stats, zt_df, zb_df


def save_to_excel(stats: dict, date: str = None, zt_df: pd.DataFrame = None, zb_df: pd.DataFrame = None):
    """保存到Excel"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    filename = f"market_stats_{date}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        summary_df = pd.DataFrame([stats])
        # 调整列顺序
        cols = ["日期", "总体涨跌比", "昨日涨停红盘比例", "昨板今均", "做连板收益",
                "连板个数", "涨停", "曾涨停", "炸板率", "跌停", "跌幅-5%以上", "高度板"]
        summary_df = summary_df[[c for c in cols if c in summary_df.columns]]
        summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
        
        if zt_df is not None and not zt_df.empty:
            zt_df.to_excel(writer, sheet_name='涨停明细', index=False)
        
        if zb_df is not None and not zb_df.empty:
            zb_df.to_excel(writer, sheet_name='炸板明细', index=False)
    
    print(f"\n数据已保存到: {filename}")
    return filename


def main():
    """主函数"""
    date = datetime.now().strftime("%Y%m%d")
    print(f"=== A股涨停情绪监控 {date} ===\n")
    
    stats, zt_df, zb_df = calculate_stats(date)
    
    print("\n=== 统计结果 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    save_to_excel(stats, date, zt_df, zb_df)
    print(f"\n完成！")


if __name__ == "__main__":
    main()