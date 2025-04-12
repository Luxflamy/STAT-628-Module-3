import pandas as pd
from pathlib import Path

def filter_us_stations(input_csv, output_csv=None):
    """
    从CSV文件中提取station_id以US开头的行
    
    参数:
        input_csv: 输入CSV文件路径
        output_csv: 可选，输出CSV文件路径。如果为None，则只返回DataFrame不保存
    """
    # 读取CSV文件
    df = pd.read_csv(input_csv)
    
    # 过滤以US开头的行
    us_stations = df[df['station_id'].str.startswith('USW')]
    

    count_usw_stations = us_stations.shape[0]
    print(f"找到 {count_usw_stations} 个以USW开头的站点。")
    
    if output_csv:
        us_stations.to_csv(output_csv, index=False)
        print(f"已保存过滤后的数据到 {output_csv}")
    
    return us_stations

# 使用示例
input_file = 'ghcnd-stations.csv'  # 你的输入CSV文件
output_file = 'us_stations.csv'    # 输出文件(可选)

# 调用函数
result = filter_us_stations(input_file, output_file)

# 显示前几行
print("过滤后的数据示例:")
print(result.head())


# 读取 CSV 文件
df = pd.read_csv("us_stations.csv")

# 筛选 name 或 additional_info 列中包含独立 " AP" 的行
ap_stations = df[
    df["name"].str.contains(r'\bAP\b', case=False, regex=True, na=False) |
    df["additional_info"].str.contains(r'\bAP\b', case=False, regex=True, na=False)
]

# 输出结果
print("包含 'AP' 的站点：")
print(ap_stations)

# 保存到新 CSV（可选）
ap_stations.to_csv("us_ap_stations.csv", index=False)
print("已保存到 us_ap_stations.csv")