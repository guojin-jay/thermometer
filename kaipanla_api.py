#!/usr/bin/env python3
"""
开盘啦数据接口
通过分析开盘啦网页/API获取涨停数据
"""

import requests
import json
import pandas as pd
from datetime import datetime


def get_kaipanla_zt(date: str = None) -> pd.DataFrame:
    """
    从开盘啦获取涨停数据
    开盘啦API: https://apphq.longhuvip.com/w1/api/index.php
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    # 开盘啦的API接口
    url = "https://apphq.longhuvip.com/w1/api/index.php"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.kaipanla.com",
        "Referer": "https://www.kaipanla.com/",
    }
    
    # 涨停池数据
    data = {
        "c": "Stock",
        "a": "ZTPool",
        "Date": date,
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"请求失败: {response.status_code}")
            return pd.DataFrame()
        
        result = response.json()
        
        if result.get("st") != 1:
            print(f"API返回错误: {result.get('msg', '未知错误')}")
            return pd.DataFrame()
        
        # 解析数据
        stock_list = result.get("list", [])
        
        data_list = []
        for item in stock_list:
            data_list.append({
                "代码": item.get("Code", ""),
                "名称": item.get("Name", ""),
                "涨停时间": item.get("ZTTime", ""),
                "涨停价": item.get("Price", 0),
                "连板数": item.get("LB", 0),
                "涨停原因": item.get("Reason", ""),
                "所属概念": item.get("Concept", ""),
                "封单金额": item.get("FDE", 0),  # 封单金额（万）
                "换手率": item.get("HS", 0),
                "流通市值": item.get("LTSZ", 0),
            })
        
        df = pd.DataFrame(data_list)
        return df
        
    except Exception as e:
        print(f"获取开盘啦涨停数据失败: {e}")
        return pd.DataFrame()


def get_kaipanla_zb(date: str = None) -> pd.DataFrame:
    """获取炸板数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    url = "https://apphq.longhuvip.com/w1/api/index.php"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.kaipanla.com/",
    }
    
    data = {
        "c": "Stock",
        "a": "ZBPool",  # 炸板池
        "Date": date,
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        response.encoding = 'utf-8'
        result = response.json()
        
        if result.get("st") != 1:
            return pd.DataFrame()
        
        stock_list = result.get("list", [])
        data_list = []
        for item in stock_list:
            data_list.append({
                "代码": item.get("Code", ""),
                "名称": item.get("Name", ""),
                "炸板时间": item.get("ZBTime", ""),
                "最新价": item.get("Price", 0),
                "涨跌幅": item.get("ZDF", 0),
            })
        
        return pd.DataFrame(data_list)
        
    except Exception as e:
        print(f"获取炸板数据失败: {e}")
        return pd.DataFrame()


def get_kaipanla_dt(date: str = None) -> pd.DataFrame:
    """获取跌停数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    url = "https://apphq.longhuvip.com/w1/api/index.php"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.kaipanla.com/",
    }
    
    data = {
        "c": "Stock",
        "a": "DTPool",  # 跌停池
        "Date": date,
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        response.encoding = 'utf-8'
        result = response.json()
        
        if result.get("st") != 1:
            return pd.DataFrame()
        
        stock_list = result.get("list", [])
        data_list = []
        for item in stock_list:
            data_list.append({
                "代码": item.get("Code", ""),
                "名称": item.get("Name", ""),
                "跌停时间": item.get("DTTime", ""),
                "最新价": item.get("Price", 0),
            })
        
        return pd.DataFrame(data_list)
        
    except Exception as e:
        print(f"获取跌停数据失败: {e}")
        return pd.DataFrame()


def get_kaipanla_prev_zt_return(date: str = None) -> dict:
    """获取昨日涨停今日收益（开盘啦数据）"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    from datetime import timedelta
    yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
    
    # 获取昨日涨停股
    prev_zt = get_kaipanla_zt(yesterday)
    
    if prev_zt.empty:
        return {"昨日涨停溢价": "N/A", "昨板今均": "N/A"}
    
    # 获取今日行情（用开盘啦的今日涨停数据来反推）
    today_data = get_kaipanla_zt(date)
    
    # 简化处理：假设昨日涨停股今日表现
    # 实际应该获取完整的今日行情数据
    return {"昨日涨停溢价": "需手动计算", "昨板今均": "需手动计算"}


if __name__ == "__main__":
    # 测试
    date = datetime.now().strftime("%Y%m%d")
    print(f"测试获取 {date} 的开盘啦数据...")
    
    zt_df = get_kaipanla_zt(date)
    print(f"\n涨停数据: {len(zt_df)} 条")
    if not zt_df.empty:
        print(zt_df.head())
    
    zb_df = get_kaipanla_zb(date)
    print(f"\n炸板数据: {len(zb_df)} 条")
    
    dt_df = get_kaipanla_dt(date)
    print(f"\n跌停数据: {len(dt_df)} 条")
