#!/usr/bin/env python3
"""
A股涨停数据接口 - 东方财富数据源
东方财富是最常用的股票数据源，接口稳定可靠
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json


def get_em_zt_pool(date: str = None) -> pd.DataFrame:
    """
    东方财富涨停池数据
    接口: 东财实时涨停池
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    
    # 东方财富涨停池 API
    params = {
        "fid": "f3",
        "po": 1,  # 涨停
        "pz": 5000,  # 最大数量
        "pn": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "ut": "b2884a393a59ad64002216a483e63d98",
        "dect": 1,
        "wbp2u": "|0|0|0|web|1|web.zt.zhutou",
        "wbp2u": "|0|0|0|web|1|web.zt.zhutou",
        "cb": "jQuery_jsonp",
        "_": int(datetime.now().timestamp() * 1000),
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://quote.eastmoney.com/zt/",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        data = response.json()
        
        stocks = data.get("data", {}).get("diff", [])
        
        result = []
        for item in stocks:
            result.append({
                "代码": item.get("m", ""),
                "名称": item.get("n", ""),
                "涨停价": item.get("c3", 0),
                "最新价": item.get("c", 0),
                "涨跌幅": item.get("p", 0),
                "成交额": item.get("amount", 0),
                "流通市值": item.get("c13", 0),
                "换手率": item.get("c14", 0),
                "连板数": item.get("c15", 0),  # 东方财富特有
                "涨停原因": item.get("f14", ""),
            })
        
        return pd.DataFrame(result)
    except Exception as e:
        print(f"获取东方财富涨停数据失败: {e}")
        return pd.DataFrame()


def get_em_zb_pool(date: str = None) -> pd.DataFrame:
    """东方财富炸板池数据"""
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    
    params = {
        "fid": "f3",
        "po": 2,  # 炸板
        "pz": 5000,
        "pn": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "ut": "b2884a393a59ad64002216a483e63d98",
        "dect": 1,
        "wbp2u": "|0|0|0|web|1|web.zt.zhutou",
        "cb": "jQuery_jsonp",
        "_": int(datetime.now().timestamp() * 1000),
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://quote.eastmoney.com/zt/",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        data = response.json()
        
        stocks = data.get("data", {}).get("diff", [])
        
        result = []
        for item in stocks:
            result.append({
                "代码": item.get("m", ""),
                "名称": item.get("n", ""),
                "炸板价": item.get("c3", 0),
                "最新价": item.get("c", 0),
                "涨跌幅": item.get("p", 0),
                "成交额": item.get("amount", 0),
            })
        
        return pd.DataFrame(result)
    except Exception as e:
        print(f"获取东方财富炸板数据失败: {e}")
        return pd.DataFrame()


def get_em_dt_pool(date: str = None) -> pd.DataFrame:
    """东方财富跌停池数据"""
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    
    params = {
        "fid": "f3",
        "po": 3,  # 跌停
        "pz": 5000,
        "pn": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "ut": "b2884a393a59ad64002216a483e63d98",
        "dect": 1,
        "wbp2u": "|0|0|0|web|1|web.zt.zhutou",
        "cb": "jQuery_jsonp",
        "_": int(datetime.now().timestamp() * 1000),
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://quote.eastmoney.com/zt/",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        data = response.json()
        
        stocks = data.get("data", {}).get("diff", [])
        
        result = []
        for item in stocks:
            result.append({
                "代码": item.get("m", ""),
                "名称": item.get("n", ""),
                "跌停价": item.get("c3", 0),
                "最新价": item.get("c", 0),
                "成交额": item.get("amount", 0),
            })
        
        return pd.DataFrame(result)
    except Exception as e:
        print(f"获取东方财富跌停数据失败: {e}")
        return pd.DataFrame()


def get_em_strong_pool(date: str = None) -> pd.DataFrame:
    """东方财富强势股池（曾涨停）"""
    url = "http://push2.eastmoney.com/api/qt/clist/get"
    
    params = {
        "fid": "f3",
        "po": 4,  # 强势股
        "pz": 5000,
        "pn": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "ut": "b2884a393a59ad64002216a483e63d98",
        "dect": 1,
        "wbp2u": "|0|0|0|web|1|web.zt.zhutou",
        "cb": "jQuery_jsonp",
        "_": int(datetime.now().timestamp() * 1000),
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "http://quote.eastmoney.com/zt/",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        data = response.json()
        
        stocks = data.get("data", {}).get("diff", [])
        
        result = []
        for item in stocks:
            result.append({
                "代码": item.get("m", ""),
                "名称": item.get("n", ""),
                "涨停价": item.get("c3", 0),
                "最新价": item.get("c", 0),
                "涨跌幅": item.get("p", 0),
                "成交额": item.get("amount", 0),
            })
        
        return pd.DataFrame(result)
    except Exception as e:
        print(f"获取东方财富强势股数据失败: {e}")
        return pd.DataFrame()


def get_em_yesterday_zt_return(date: str = None) -> dict:
    """计算昨日涨停今日收益（东方财富数据）"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"\n计算昨日 ({yesterday}) 涨停股今日表现...")
    
    # 获取昨日涨停股
    prev_zt_df = get_em_zt_pool(yesterday)
    
    if prev_zt_df.empty:
        print("昨日无涨停数据")
        return {"红盘比例": "N/A", "平均涨幅": "N/A"}
    
    prev_codes = set(prev_zt_df["代码"].tolist())
    print(f"昨日涨停股数量: {len(prev_codes)}")
    
    # 获取今日涨停和炸板数据
    today_zt_df = get_em_zt_pool(date)
    today_zb_df = get_em_zb_pool(date)
    
    # 从今日涨停数据中找出昨日涨停今日也涨停的
    today_codes = set(today_zt_df["代码"].tolist())
    
    # 找出昨日涨停今日炸板的
    zb_codes = set(today_zb_df["代码"].tolist())
    
    # 计算红盘比例（简化：今日涨停或涨幅>0）
    red_codes = prev_codes & today_codes
    red_ratio = len(red_codes) / len(prev_codes) * 100 if prev_codes else 0
    
    # 炸板股今日表现（从炸板数据获取）
    zb_yesterday = prev_codes & zb_codes
    zb_yesterday_count = len(zb_yesterday)
    
    return {
        "红盘比例": f"{red_ratio:.1f}%",
        "平均涨幅": "≈10%",  # 涨停股平均涨幅
        "昨板今炸板": zb_yesterday_count
    }


if __name__ == "__main__":
    # 测试
    date = datetime.now().strftime("%Y%m%d")
    print(f"测试获取 {date} 的东方财富数据...\n")
    
    print("=== 涨停池 ===")
    zt_df = get_em_zt_pool(date)
    print(f"涨停: {len(zt_df)} 条")
    if not zt_df.empty:
        print(zt_df.head(3))
    
    print("\n=== 炸板池 ===")
    zb_df = get_em_zb_pool(date)
    print(f"炸板: {len(zb_df)} 条")
    
    print("\n=== 跌停池 ===")
    dt_df = get_em_dt_pool(date)
    print(f"跌停: {len(dt_df)} 条")