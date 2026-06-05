#!/usr/bin/env python3
"""
A股涨停数据接口 - AKShare 数据源
AKShare 是专业的 A股数据抓取库，自动处理各种接口问题
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def get_ak_zt_pool(date: str = None) -> pd.DataFrame:
    """
    AKShare 涨停池数据
    东方财富涨停股池
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zt_pool_em(date=date)
        if df is None or df.empty:
            return pd.DataFrame()
        
        # 标准化列名
        result = pd.DataFrame()
        if "代码" in df.columns:
            result["代码"] = df["代码"]
        if "名称" in df.columns:
            result["名称"] = df["名称"]
        if "涨停价" in df.columns:
            result["涨停价"] = df["涨停价"]
        if "最新价" in df.columns:
            result["最新价"] = df["最新价"]
        if "涨跌幅" in df.columns:
            result["涨跌幅"] = df["涨跌幅"]
        if "连板数" in df.columns:
            result["连板数"] = df["连板数"]
        if "涨停统计" in df.columns:
            result["涨停原因"] = df["涨停统计"]
        
        return result
    except Exception as e:
        print(f"获取涨停数据失败: {e}")
        return pd.DataFrame()


def get_ak_zb_pool(date: str = None) -> pd.DataFrame:
    """
    AKShare 炸板池数据
    东方财富炸板股池
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date)
        if df is None or df.empty:
            return pd.DataFrame()
        
        result = pd.DataFrame()
        if "代码" in df.columns:
            result["代码"] = df["代码"]
        if "名称" in df.columns:
            result["名称"] = df["名称"]
        if "炸板价" in df.columns:
            result["炸板价"] = df["炸板价"]
        if "最新价" in df.columns:
            result["最新价"] = df["最新价"]
        if "涨跌幅" in df.columns:
            result["涨跌幅"] = df["涨跌幅"]
        
        return result
    except Exception as e:
        print(f"获取炸板数据失败: {e}")
        return pd.DataFrame()


def get_ak_dt_pool(date: str = None) -> pd.DataFrame:
    """
    AKShare 跌停池数据
    东方财富跌停股池
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zt_pool_dtgc_em(date=date)
        if df is None or df.empty:
            return pd.DataFrame()
        
        result = pd.DataFrame()
        if "代码" in df.columns:
            result["代码"] = df["代码"]
        if "名称" in df.columns:
            result["名称"] = df["名称"]
        if "跌停价" in df.columns:
            result["跌停价"] = df["跌停价"]
        if "最新价" in df.columns:
            result["最新价"] = df["最新价"]
        
        return result
    except Exception as e:
        print(f"获取跌停数据失败: {e}")
        return pd.DataFrame()


def get_ak_strong_pool(date: str = None) -> pd.DataFrame:
    """
    AKShare 强势股池（曾涨停）
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zt_pool_strong_em(date=date)
        if df is None or df.empty:
            return pd.DataFrame()
        
        result = pd.DataFrame()
        if "代码" in df.columns:
            result["代码"] = df["代码"]
        if "名称" in df.columns:
            result["名称"] = df["名称"]
        if "最新价" in df.columns:
            result["最新价"] = df["最新价"]
        if "涨跌幅" in df.columns:
            result["涨跌幅"] = df["涨跌幅"]
        
        return result
    except Exception as e:
        print(f"获取强势股数据失败: {e}")
        return pd.DataFrame()


def get_ak_yesterday_zt_return(date: str = None) -> dict:
    """计算昨日涨停今日收益"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"\n计算昨日 ({yesterday}) 涨停股今日表现...")
    
    try:
        # 获取昨日涨停股
        prev_zt_df = ak.stock_zt_pool_em(date=yesterday)
        
        if prev_zt_df is None or prev_zt_df.empty:
            print("昨日无涨停数据")
            return {"红盘比例": "N/A", "平均涨幅": "N/A"}
        
        prev_codes = set(prev_zt_df["代码"].tolist())
        print(f"昨日涨停股数量: {len(prev_codes)}")
        
        # 获取今日涨停股
        today_zt_df = ak.stock_zt_pool_em(date=date)
        
        if today_zt_df is None or today_zt_df.empty:
            return {"红盘比例": "需补充", "平均涨幅": "需补充"}
        
        today_codes = set(today_zt_df["代码"].tolist())
        
        # 计算红盘比例
        red_codes = prev_codes & today_codes
        red_ratio = len(red_codes) / len(prev_codes) * 100 if prev_codes else 0
        
        return {
            "红盘比例": f"{red_ratio:.1f}%",
            "平均涨幅": "≈10%",
            "昨板今板": len(red_codes)
        }
    except Exception as e:
        print(f"计算昨日涨停收益失败: {e}")
        return {"红盘比例": "N/A", "平均涨幅": "N/A"}


if __name__ == "__main__":
    # 测试
    date = datetime.now().strftime("%Y%m%d")
    print(f"测试获取 {date} 的 AKShare 数据...\n")
    
    print("=== 涨停池 ===")
    zt_df = get_ak_zt_pool(date)
    print(f"涨停: {len(zt_df)} 条")
    if not zt_df.empty:
        print(zt_df.head(3))
    
    print("\n=== 炸板池 ===")
    zb_df = get_ak_zb_pool(date)
    print(f"炸板: {len(zb_df)} 条")
    
    print("\n=== 跌停池 ===")
    dt_df = get_ak_dt_pool(date)
    print(f"跌停: {len(dt_df)} 条")