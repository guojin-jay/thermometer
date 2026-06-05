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


def get_market_stats_by_batch(date: str = None) -> dict:
    """
    通过涨停池和炸板池数据间接计算市场涨跌情况
    由于全市场数据接口不稳定，使用估算方法
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        # 获取涨停池（含市场统计信息）
        zt_df = ak.stock_zt_pool_em(date=date)
        
        if zt_df is None or zt_df.empty:
            return {"涨跌比": "N/A", "跌超5%": "N/A"}
        
        # 从涨停池数据中提取市场统计
        # 注意：涨停池数据本身不包含全市场涨跌信息，需要其他方式
        
        # 尝试使用指数数据
        try:
            # 上证指数数据
            sh_df = ak.stock_zh_index_daily(symbol="000001")
            if not sh_df.empty:
                latest = sh_df.iloc[-1]
                # 根据指数涨跌估算市场情绪
                change = latest.get('close', 0) / latest.get('open', 1) - 1
                change_pct = change * 100
                
                # 粗略估算涨跌家数比（基于经验公式）
                # 指数涨幅1%约等于上涨家数略多
                if change_pct > 0:
                    up_down_ratio = 1.1 + change_pct / 5  # 上涨时涨跌比 > 1
                else:
                    up_down_ratio = 0.9 + change_pct / 5   # 下跌时涨跌比 < 1
                up_down_ratio = max(0.1, up_down_ratio)
                
                return {
                    "指数涨跌": f"{change_pct:.2f}%",
                    "涨跌比": f"{up_down_ratio:.2f}"
                }
        except Exception as e:
            print(f"获取指数数据失败: {e}")
        
        return {"涨跌比": "N/A", "跌超5%": "N/A"}
        
    except Exception as e:
        print(f"获取市场统计数据失败: {e}")
        return {"涨跌比": "N/A", "跌超5%": "N/A"}


def get_yesterday_zt_performance(date: str = None) -> dict:
    """
    计算昨日涨停股今日表现
    通过对比昨日涨停池和今日涨停池/炸板池
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"\n计算昨日 ({yesterday}) 涨停股今日表现...")
    
    try:
        # 昨日涨停股
        prev_zt_df = get_zt_pool(yesterday)
        
        if prev_zt_df.empty:
            return {"红盘比例": "N/A", "昨板今均": "N/A", "做连板收益": "N/A"}
        
        prev_codes = set(prev_zt_df["代码"].tolist())
        prev_count = len(prev_codes)
        print(f"昨日涨停股数量: {prev_count}")
        
        # 昨日连板股（连板数>=2）
        if "连板数" in prev_zt_df.columns:
            prev_lb_df = prev_zt_df[prev_zt_df["连板数"] >= 2]
            prev_lb_codes = set(prev_lb_df["代码"].tolist()) if not prev_lb_df.empty else set()
            print(f"昨日连板股数量: {len(prev_lb_codes)}")
        else:
            prev_lb_codes = set()
        
        # 今日涨停股
        today_zt_df = get_zt_pool(date)
        today_zt_codes = set(today_zt_df["代码"].tolist()) if not today_zt_df.empty else set()
        
        # 今日炸板股
        today_zb_df = get_zb_pool(date)
        today_zb_codes = set(today_zb_df["代码"].tolist()) if not today_zb_df.empty else set()
        
        # 昨日涨停今日涨停（继续板）
        zt_zt_count = len(prev_codes & today_zt_codes)
        
        # 昨日涨停今日炸板
        zt_zb_count = len(prev_codes & today_zb_codes)
        
        # 昨日涨停今日平盘或回调（不在涨停也不在炸板）
        zt_other_count = prev_count - zt_zt_count - zt_zb_count
        
        # 红盘比例估算：
        # - 继续涨停算红盘
        # - 炸板算非红盘（涨幅<10%）
        # - 其他情况无法确定，简化为：继续涨停/总数量
        red_ratio = zt_zt_count / prev_count * 100 if prev_count > 0 else 0
        
        # 平均涨幅估算：
        # - 继续涨停：10%
        # - 炸板：从涨停池获取实际涨幅
        # - 其他：0%
        total_return = zt_zt_count * 10  # 继续涨停按10%算
        
        if not today_zb_df.empty:
            # 获取炸板股的涨幅
            zb_prev_zt = today_zb_df[today_zb_df["代码"].isin(prev_codes)]
            if not zb_prev_zt.empty and "涨跌幅" in zb_prev_zt.columns:
                zb_returns = zb_prev_zt["涨跌幅"].tolist()
                total_return += sum(zb_returns)
                zb_count = len(zb_returns)
            else:
                zb_count = 0
        else:
            zb_count = 0
        
        # 其他未涨停的按0涨幅算
        other_count = prev_count - zt_zt_count - zb_count
        avg_return = total_return / prev_count if prev_count > 0 else 0
        
        # 连板收益：昨日连板股今日表现
        if prev_lb_codes:
            lb_zt_count = len(prev_lb_codes & today_zt_codes)  # 继续连板
            lb_zb_count = len(prev_lb_codes & today_zb_codes)  # 连板炸板
            
            # 估算连板收益
            lb_total_return = lb_zt_count * 10
            if not today_zb_df.empty:
                zb_lb = today_zb_df[today_zb_df["代码"].isin(prev_lb_codes)]
                if not zb_lb.empty and "涨跌幅" in zb_lb.columns:
                    lb_total_return += zb_lb["涨跌幅"].sum()
            
            lb_avg_return = lb_total_return / len(prev_lb_codes) if prev_lb_codes else 0
            lb_avg_return_str = f"{lb_avg_return:.2f}%"
        else:
            lb_avg_return_str = "N/A"
        
        return {
            "红盘比例": f"{red_ratio:.1f}%",
            "昨板今均": f"{avg_return:.2f}%",
            "做连板收益": lb_avg_return_str,
            "昨板今板": zt_zt_count,
            "昨板今炸": zt_zb_count,
        }
        
    except Exception as e:
        print(f"计算昨日涨停表现失败: {e}")
        return {"红盘比例": "N/A", "昨板今均": "N/A", "做连板收益": "N/A"}


def calculate_stats(date: str = None) -> dict:
    """计算市场情绪指标"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"正在获取 {date} 的市场数据...\n")
    
    # ========== 基础数据 ==========
    zt_df = get_zt_pool(date)
    zb_df = get_zb_pool(date)
    dt_df = get_dt_pool(date)
    
    # ========== 1. 涨停炸板统计 ==========
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
    
    # ========== 2. 昨日涨停表现 ==========
    prev_stats = get_yesterday_zt_performance(date)
    
    # ========== 3. 总体涨跌比 ==========
    # 由于全市场数据接口不稳定，暂时用涨停池数据估算
    market_stats = get_market_stats_by_batch(date)
    
    # 估算总体涨跌比（基于经验）
    # 涨停多说明市场强，但需要结合炸板率判断
    # 简化：涨停/跌停 比值作为参考
    zt_dt_ratio = zt_count / dt_count if dt_count > 0 else zt_count
    
    stats = {
        "日期": date,
        "总体涨跌比": f"{zt_dt_ratio:.2f}",  # 简化为涨停/跌停比
        "昨日涨停红盘比例": prev_stats.get("红盘比例", "N/A"),
        "昨板今均": prev_stats.get("昨板今均", "N/A"),
        "做连板收益": prev_stats.get("做连板收益", "N/A"),
        "连板个数": lb_ge_2,
        "涨停": zt_count,
        "曾涨停": strong_count,
        "炸板率": f"{zb_rate:.2f}%",
        "跌停": dt_count,
        "跌幅-5%以上": "需补充",  # 需要全市场数据
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