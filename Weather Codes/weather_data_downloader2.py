import pandas as pd
import requests
from datetime import datetime
import os

def fetch_weather_data(station_id, start_date, end_date, data_types, units="metric"):
    """
    从NCEI API获取气象数据
    """
    base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
    
    params = {
        "dataset": "daily-summaries",
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "dataTypes": ",".join(data_types),
        "units": units,
        "format": "json",
        "includeStationName": "true",
        "includeStationLocation": "true"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{base_url}?{query_string}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        
        # 规范化列名和顺序
        if not df.empty:
            df = standardize_columns(df)
            
        return df
    except Exception as e:
        print(f"获取数据失败(站点{station_id}): {e}")
        return None

def standardize_columns(df):
    """
    规范数据列顺序和格式
    """
    # 定义固定顺序的列名（优先显示的列）
    priority_columns = [
        'STATION', 'NAME', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION'
    ]
    
    # 获取实际存在的优先列
    existing_priority = [col for col in priority_columns if col in df.columns]
    
    # 获取其他列（气象数据列）
    other_columns = [col for col in df.columns if col not in existing_priority]
    
    # 按类型对气象数据列排序（温度、降水、风速等）
    sorted_other_columns = sorted(other_columns, key=lambda x: (
        0 if x.startswith('T') else  # 温度相关
        1 if x.startswith('PRCP') or x.startswith('SNOW') else  # 降水
        2 if x.startswith('AWND') or x.startswith('WSF') or x.startswith('GUST') else  # 风速
        3 if x.startswith('RH') or x.startswith('VIS') else  # 湿度和能见度
        4 if x.startswith('WT') else  # 天气现象
        5  # 其他
    ))
    
    # 合并列顺序
    final_columns = existing_priority + sorted_other_columns
    
    # 应用新列顺序
    df = df[final_columns]
    
    # 统一日期格式
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE']).dt.strftime('%Y-%m-%d')
    
    return df

def save_to_csv(df, station_name, start_date, end_date, output_dir="weather_data"):
    """
    将数据保存为CSV文件
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 清理站名中的特殊字符
    clean_name = "".join(c for c in station_name if c.isalnum() or c in (' ', '-', '_'))
    
    # 格式化日期范围
    start_str = start_date.replace("-", "")
    end_str = end_date.replace("-", "")
    
    # 生成文件名
    filename = f"{clean_name}-{start_str}-{end_str}.csv"
    filepath = os.path.join(output_dir, filename)
    
    df.to_csv(filepath, index=False)
    print(f"已保存: {filepath}")

def main():
    # 配置参数
    cities = {
        # "NewYork": "USW00094728",    # 纽约中央公园
        "Chicago": "USW00094846",    # 芝加哥奥黑尔
        # "LosAngeles": "USW00023174", # 洛杉矶国际机场
        # 添加更多城市...
    }
    
    # 用户输入
    start_date = "2020-01-01"
    end_date = "2025-01-31"
    
    # 选择气象变量
    data_types = [
        "TMAX", "TMIN", "TAVG",    # 温度
        "PRCP", "SNOW",             # 降水
        "AWND", "WSF2", "WSF5",     # 风速
        "RH", "VIS",                # 湿度和能见度
        "WT01", "WT03"              # 天气现象(雾,雷雨)
    ]
    
    print(f"\n开始获取{start_date}至{end_date}的气象数据...")
    
    # 获取并保存每个城市的数据
    for city_name, station_id in cities.items():
        print(f"\n正在处理: {city_name} ({station_id})")
        
        df = fetch_weather_data(station_id, start_date, end_date, data_types)
        
        if df is not None and not df.empty:
            # 获取站名用于文件名
            station_name = df['NAME'].iloc[0] if 'NAME' in df.columns else city_name
            save_to_csv(df, station_name, start_date, end_date)
        else:
            print(f"未获取到{city_name}的有效数据")
    
    print("\n所有城市数据处理完成!")

if __name__ == "__main__":
    main()