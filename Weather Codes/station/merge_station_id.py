import pandas as pd
from pathlib import Path
import re

# 设置文件路径
station_dir = Path("station")
airport_path = station_dir / "airport_id.csv"
usap_path = station_dir / "us_ap_stations.csv"
output_path = station_dir / "final_station_id.csv"

# 读取数据
airport_df = pd.read_csv(airport_path)
usap_df = pd.read_csv(usap_path)

# 预处理函数
def clean_city_name(name):
    """提取机场名称中的城市核心部分"""
    # 去除机场类型标识
    name = re.sub(
        r'\b(AP|MUNI|RGNL|CO|FLD|MEMORIAL|INTL|EXEC|COUNTY|AIRPORT|FAA|WSO)\b', 
        '', 
        name, 
        flags=re.IGNORECASE
    )
    # 保留主要城市名部分
    city = name.split()[0] if len(name.split()) > 0 else name
    return city.strip().lower().replace(" ", "").replace("-", "")

# 预处理城市名称
airport_df['city_clean'] = airport_df['CITY'].apply(clean_city_name)
usap_df['city_clean'] = usap_df['name'].apply(clean_city_name)

# 合并数据集（内连接）
merged = pd.merge(
    usap_df,
    airport_df,
    how='inner',
    left_on=['state', 'city_clean'],
    right_on=['STATE', 'city_clean']
)

# 选择需要的列并重命名
result = merged[[
    'station_id', 'AIRPORT_ID', 'state', 'CITY', 'IATA_CODE',
    'longitude', 'latitude', 'elevation'
]].drop_duplicates().reset_index(drop=True)

result.columns = [
    'station_id', 'airport_id', 'state', 'city', 'IATA_CODE',
    'longitude', 'latitude', 'elevation'
]

# 保存结果
result.to_csv(output_path, index=False)
print(f"合并完成，共匹配到 {len(result)} 条记录")
print(f"结果已保存到 {output_path}")