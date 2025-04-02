import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# 设置页面
st.set_page_config(page_title="航空气象数据分析", layout="wide")
st.title("气象条件与航班延误关系分析")

# 解释数据来源
st.markdown("""
数据来源: [美国国家环境信息中心(NCEI)](https://www.ncei.noaa.gov/)
""")

# 侧边栏参数设置
with st.sidebar:
    st.header("查询参数")
    
    # 设置默认日期（最近30天）
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    # 日期选择
    start_date = st.date_input("开始日期", start_date)
    end_date = st.date_input("结束日期", end_date)
    
    # 气象站选择（机场气象站）
    st.markdown("### 机场气象站ID")
    col1, col2 = st.columns(2)
    with col1:
        station = st.text_input("主气象站", "USW00094846", 
                              help="例如：USW00094846（芝加哥奥黑尔机场）")
    with col2:
        compare_station = st.text_input("对比气象站(可选)", "",
                                      help="输入另一个站点ID进行比较")
    
    # 单位选择
    units = st.radio("单位系统", ["metric", "standard"], index=0)
    
    # 气象变量选择
    st.markdown("### 气象变量")
    basic_vars = st.multiselect(
        "基本变量",
        ["TMAX", "TMIN", "TAVG", "PRCP"],
        ["TMAX", "TMIN"],
        help="温度、降水等基本气象数据"
    )
    
    aviation_vars = st.multiselect(
        "航空相关变量",
        ["AWND", "WSF2", "WSF5", "RH", "VIS", "GUST", "SNOW", "WT01"],
        ["AWND", "VIS", "RH"],
        help="""
        AWND:平均风速, WSF2:最大风速(2分钟), WSF5:最大风速(5分钟)
        RH:相对湿度, VIS:能见度, GUST:阵风, SNOW:积雪, WT01:雾
        """
    )
    
    # 提交按钮
    submit_button = st.button("获取气象数据")

# 构建API请求URL
def build_url(station, start_date, end_date, data_types, units="metric"):
    base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
    
    params = {
        "dataset": "daily-summaries",
        "stations": station,
        "startDate": start_date,
        "endDate": end_date,
        "dataTypes": ",".join(data_types),
        "units": units,
        "format": "json",
        "includeStationName": "true",
        "includeStationLocation": "true"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"

# 获取数据
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None

# 主界面
if submit_button:
    st.subheader(f"{start_date} 至 {end_date} 的气象数据分析")
    
    # 显示加载状态
    with st.spinner("正在获取数据..."):
        all_vars = basic_vars + aviation_vars
        url = build_url(station, start_date, end_date, all_vars, units)
        df = fetch_data(url)
        
        if compare_station:
            compare_url = build_url(compare_station, start_date, end_date, all_vars, units)
            df_compare = fetch_data(compare_url)
            if df_compare is not None:
                df_compare['STATION'] = df_compare['STATION'] + " (对比)"
    
    if df is not None and not df.empty:
        st.success(f"成功获取 {len(df)} 条记录")
        
        # 合并对比数据
        if compare_station and df_compare is not None and not df_compare.empty:
            df = pd.concat([df, df_compare])
            st.success(f"成功获取对比站点 {len(df_compare)} 条记录")
        
        # 显示站点信息
        if 'STATION' in df.columns and 'NAME' in df.columns:
            st.markdown("### 气象站信息")
            cols = st.columns(3)
            with cols[0]:
                st.metric("气象站ID", df['STATION'].iloc[0])
            with cols[1]:
                st.metric("气象站名称", df['NAME'].iloc[0])
            with cols[2]:
                st.metric("位置", f"{df['LATITUDE'].iloc[0]}, {df['LONGITUDE'].iloc[0]}")
        
        # 数据预处理
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # 转换单位标签
        unit_labels = {
            "TMAX": "°C" if units == "metric" else "°F",
            "TMIN": "°C" if units == "metric" else "°F",
            "TAVG": "°C" if units == "metric" else "°F",
            "PRCP": "mm" if units == "metric" else "in",
            "AWND": "m/s" if units == "metric" else "mph",
            "WSF2": "m/s" if units == "metric" else "mph",
            "WSF5": "m/s" if units == "metric" else "mph",
            "GUST": "m/s" if units == "metric" else "mph",
            "RH": "%",
            "VIS": "km" if units == "metric" else "mi",
            "SNOW": "mm" if units == "metric" else "in"
        }
        
        # 转换数值类型
        numeric_cols = all_vars + ['LATITUDE', 'LONGITUDE']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 创建选项卡
        tab1, tab2, tab3 = st.tabs(["温度分析", "航空气象分析", "原始数据"])
        
        with tab1:
            # 温度数据可视化
            temp_cols = [col for col in ['TMAX', 'TMIN', 'TAVG'] if col in df.columns]
            if temp_cols:
                fig_temp = px.line(df, x='DATE', y=temp_cols,
                                 color='STATION' if compare_station else None,
                                 title='每日温度变化',
                                 labels={'value': f'温度 ({unit_labels["TMAX"]})', 'DATE': '日期'},
                                 color_discrete_map={
                                     'TMAX': 'red',
                                     'TMIN': 'blue',
                                     'TAVG': 'green'
                                 })
                fig_temp.update_traces(mode='lines+markers')
                st.plotly_chart(fig_temp, use_container_width=True)
            
            # 温度分布箱线图
            if temp_cols:
                fig_box = px.box(df, y=temp_cols, 
                               color='STATION' if compare_station else None,
                               title='温度分布统计',
                               labels={'value': f'温度 ({unit_labels["TMAX"]})'})
                st.plotly_chart(fig_box, use_container_width=True)
        
        with tab2:
            # 风速分析
            wind_cols = [col for col in ['AWND', 'WSF2', 'WSF5', 'GUST'] if col in df.columns]
            if wind_cols:
                st.markdown("### 风速分析")
                fig_wind = px.line(df, x='DATE', y=wind_cols,
                                  color='STATION' if compare_station else None,
                                  title='风速变化',
                                  labels={'value': f'风速 ({unit_labels["AWND"]})', 'DATE': '日期'})
                st.plotly_chart(fig_wind, use_container_width=True)
                
                # 风速玫瑰图
                if 'AWND' in df.columns and 'LATITUDE' in df.columns:
                    st.markdown("#### 风向频率分析")
                    if 'WDF2' in df.columns:  # 风向数据
                        fig_windrose = px.bar_polar(df, r='AWND', theta='WDF2',
                                                   color='STATION' if compare_station else None,
                                                   title='风速风向玫瑰图',
                                                   labels={'r': f'风速 ({unit_labels["AWND"]})'})
                        st.plotly_chart(fig_windrose, use_container_width=True)
                    else:
                        st.warning("未获取到风向数据(WDF2)")
            
            # 能见度分析
            if 'VIS' in df.columns:
                st.markdown("### 能见度分析")
                fig_vis = px.line(df, x='DATE', y='VIS',
                                color='STATION' if compare_station else None,
                                title='能见度变化',
                                labels={'VIS': f'能见度 ({unit_labels["VIS"]})', 'DATE': '日期'})
                st.plotly_chart(fig_vis, use_container_width=True)
            
            # 湿度分析
            if 'RH' in df.columns:
                st.markdown("### 相对湿度分析")
                fig_rh = px.line(df, x='DATE', y='RH',
                               color='STATION' if compare_station else None,
                               title='相对湿度变化',
                               labels={'RH': '相对湿度 (%)', 'DATE': '日期'})
                st.plotly_chart(fig_rh, use_container_width=True)
            
            # 天气现象分析
            weather_codes = [col for col in df.columns if col.startswith('WT')]
            if weather_codes:
                st.markdown("### 恶劣天气现象")
                weather_df = df[['DATE', 'STATION'] + weather_codes].melt(
                    id_vars=['DATE', 'STATION'], var_name='天气现象', value_name='是否出现')
                weather_df = weather_df[weather_df['是否出现'] == 1]
                
                if not weather_df.empty:
                    fig_weather = px.histogram(weather_df, x='DATE', color='天气现象',
                                             facet_row='STATION' if compare_station else None,
                                             title='恶劣天气现象发生情况',
                                             labels={'count': '发生次数'})
                    st.plotly_chart(fig_weather, use_container_width=True)
                else:
                    st.info("查询期间未记录到恶劣天气现象")
        
        with tab3:
            # 显示原始数据
            st.dataframe(df)
            
            # 数据下载按钮
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="下载数据为CSV",
                data=csv,
                file_name=f"weather_data_{start_date}_{end_date}.csv",
                mime='text/csv'
            )
    
    elif df is not None and df.empty:
        st.warning("没有找到符合条件的数据")
    else:
        st.error("无法获取数据，请检查参数或稍后再试")

else:
    st.info("请在侧边栏设置查询参数并点击'获取气象数据'按钮")
    st.markdown("""
    ### 常见机场气象站ID:
    | 机场 | 气象站ID |
    |------|----------|
    | 亚特兰大哈茨菲尔德 | USW00013874 |
    | 芝加哥奥黑尔 | USW00094846 |
    | 达拉斯/沃斯堡 | USW00013960 |
    | 丹佛国际 | USW00003017 |
    | 洛杉矶国际 | USW00023174 |
    | 纽约肯尼迪 | USW00094789 |
    | 旧金山国际 | USW00023234 |
    | 西雅图-塔科马 | USW00024233 |
    
    更多站点可通过[NCEI站点搜索](https://www.ncei.noaa.gov/access/search/)查找
    """)

# 添加航空气象知识
with st.expander("航空气象知识"):
    st.markdown("""
    ### 影响航班延误的主要气象因素:
    
    1. **风速和风向**
    - 强风(特别是侧风)会影响飞机起降
    - 通常商业航班最大允许侧风: 20-35节(10-18 m/s)
    
    2. **能见度**
    - 低能见度(<1.6 km)可能导致航班延误或取消
    - 雾(WT01)、雨雪等都会降低能见度
    
    3. **降水**
    - 强降水需要更长的跑道制动距离
    - 冻雨可能导致飞机积冰
    
    4. **温度**
    - 极端高温会降低飞机升力
    - 低温可能影响飞机系统
    
    5. **雷暴**
    - 包含闪电、湍流、冰雹等多种危险
    
    ### 关键气象变量解释:
    - **AWND**: 平均风速 - 持续风力的衡量
    - **WSF2/WSF5**: 2分钟/5分钟最大风速 - 突风强度
    - **GUST**: 阵风 - 瞬时风速峰值
    - **VIS**: 能见度 - 肉眼可见的最远距离
    - **RH**: 相对湿度 - 高湿度易形成雾
    - **WT01**: 雾 - 能见度<1 km的天气现象
    """)