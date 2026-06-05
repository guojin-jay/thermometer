#!/usr/bin/env python3
"""
A股涨停数据接口 - 辅助函数
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def get_stock_minute_data(symbol: str, date: str = None) -> pd.DataFrame:
    """
    获取股票分钟级行情数据
    """
    try:
        # 格式化股票代码
        if symbol.startswith("00") or symbol.startswith("60") or symbol.startswith("30"):
            symbol = f"{symbol}.SZ" if symbol.startswith("00") or symbol.startswith("30") else f"{symbol}.SH"
        
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=date, end_date=date, adjust="qfq")
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


def get_stock_realtime_quote(symbol: str) -> dict:
    """
    获取股票实时行情（单个）
    使用东方财富接口
    """
    try:
        url = f"http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": f"0.{symbol}" if symbol.startswith("00") or symbol.startswith("30") else f"1.{symbol}",
            "ut": "fa5fd1943c7b386f172d6893dbbd3d2c",
            "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f107,f169,f170,f171",
            "cb": "jQuery_jsonp"
        }
        
        import requests
        response = requests.get(url, params=params, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        
        if data.get("data"):
            d = data["data"]
            return {
                "code": symbol,
                "price": d.get("f43", 0),  # 最新价
                "change_pct": d.get("f170", 0),  # 涨跌幅
            }
    except Exception as e:
        pass
    
    return {}


def get_down_5pct_count(date: str = None) -> int:
    """
    获取跌幅超过5%的股票数量
    使用东方财富大盘统计接口
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    try:
        # 东方财富市场概况接口
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1,
            "pz": 1,
            "np": 1,
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23,m:0+t:80+s:2048",  # 沪深A股
            "fields": "f12,f14,f3",
            "_": int(datetime.now().timestamp() * 1000),
        }
        
        import requests
        response = requests.get(url, params=params, timeout=15)
        response.encoding = 'utf-8'
        data = response.json()
        
        total = data.get("data", {}).get("total", 0)
        
        # 获取跌幅超过5%的数量
        params["fs"] = "m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23,m:0+t:80+s:2048"
        params["fi"] = "f3~-5"
        params["fields"] = "f12,f14,f3"
        
        response = requests.get(url, params=params, timeout=15)
        response.encoding = 'utf-8'
        data = response.json()
        
        down5_count = data.get("data", {}).get("total", 0)
        
        return down5_count
        
    except Exception as e:
        print(f"获取跌幅超过5%股票数量失败: {e}")
        return -1


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


if __name__ == "__main__":
    # 测试
    date = datetime.now().strftime("%Y%m%d")
    print(f"测试获取 {date} 的数据...\n")
    
    print("=== 涨停池 ===")
    zt_df = get_zt_pool(date)
    print(f"涨停: {len(zt_df)} 条")
    
    print("\n=== 炸板池 ===")
    zb_df = get_zb_pool(date)
    print(f"炸板: {len(zb_df)} 条")
    
    print("\n=== 跌停池 ===")
    dt_df = get_dt_pool(date)
    print(f"跌停: {len(dt_df)} 条")
    
    print("\n=== 跌幅超5% ===")
    down5 = get_down_5pct_count(date)
    print(f"跌幅超5%: {down5} 条")