import pandas as pd
import requests
from datetime import datetime
import os
import time
from tqdm import tqdm  # 用于显示进度条

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
        print(f"\n获取数据失败(站点{station_id}): {e}")
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

def save_monthly_data(df, iata_code, year, month, output_dir="weather_data"):
    """
    将月度数据保存为CSV文件，按照指定命名规则
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 过滤出当月数据
    df['DATE'] = pd.to_datetime(df['DATE'])
    monthly_df = df[(df['DATE'].dt.year == year) & (df['DATE'].dt.month == month)]
    
    if monthly_df.empty:
        return False
    
    # 生成文件名
    month_name = datetime(year, month, 1).strftime('%b')  # 获取月份英文缩写
    filename = f"{iata_code}_{year}_{month_name}_1.csv"
    filepath = os.path.join(output_dir, filename)
    
    # 处理同机场多个站点的情况
    counter = 1
    while os.path.exists(filepath):
        counter += 1
        filename = f"{iata_code}_{year}_{month_name}_{counter}.csv"
        filepath = os.path.join(output_dir, filename)
    
    monthly_df.to_csv(filepath, index=False)
    return True

def main():
    # 读取站点信息
    station_df = pd.read_csv('station/final_station_id.csv')
    
    # 只保留有IATA代码的站点
    station_df = station_df.dropna(subset=['IATA_CODE'])
    
    # 选择气象变量
    data_types = [
        "TMAX", "TMIN", "TAVG",    # 温度
        "PRCP", "SNOW",             # 降水
        "AWND", "WSF2", "WSF5",     # 风速
        "RH", "VIS",                # 湿度和能见度
        "WT01", "WT03"              # 天气现象(雾,雷雨)
    ]
    
    # 设置日期范围
    years = range(2021, 2025)  # 2021-2024年
    months = [5, 6, 7, 8]      # 5-8月
    
    print(f"\n开始获取气象数据(2021-2024年5-8月)...")
    
    # 遍历每个站点
    for _, row in tqdm(station_df.iterrows(), total=len(station_df), desc="处理站点"):
        station_id = row['station_id']
        iata_code = row['IATA_CODE']
        
        # 获取该站点的完整数据
        full_df = fetch_weather_data(
            station_id=station_id,
            start_date="2021-01-01",
            end_date="2024-12-31",
            data_types=data_types
        )
        
        if full_df is None or full_df.empty:
            continue
        
        # 保存每月数据
        for year in years:
            for month in months:
                saved = save_monthly_data(full_df, iata_code, year, month)
                if not saved:
                    print(f"\n警告: {iata_code} {year}-{month} 无数据")
        
        # 避免API请求过于频繁
        time.sleep(1)
    
    print("\n所有数据处理完成!")

if __name__ == "__main__":
    main()