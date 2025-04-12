import pandas as pd

def convert_stations_to_csv(input_file, output_file):
    # 定义固定宽度格式 - 根据示例数据调整这些值
    col_specs = [
        (0, 11),    # 站点ID
        (12, 20),   # 纬度
        (21, 30),   # 经度
        (31, 37),   # 海拔
        (38, 40),   # 州/省
        (41, 71),   # 站点名称
        (72, 75)    # 其他信息(如果有)
    ]
    
    # 定义列名
    column_names = ['station_id', 'latitude', 'longitude', 'elevation', 'state', 'name', 'additional_info']
    
    # 读取固定宽度文件
    df = pd.read_fwf(input_file, colspecs=col_specs, header=None, names=column_names)
    
    # 清理数据 - 去除字符串字段两端的空格
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    
    # 保存为CSV
    df.to_csv(output_file, index=False)
    print(f"文件已成功转换为 {output_file}")

# 使用示例
input_file = 'ghcnd-stations.txt'
output_file = 'ghcnd-stations.csv'
convert_stations_to_csv(input_file, output_file)