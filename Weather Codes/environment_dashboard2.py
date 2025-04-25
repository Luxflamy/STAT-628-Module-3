import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# Set up the page
st.set_page_config(page_title="Aviation Weather Data Analysis", layout="wide")
st.title("Analysis of Weather Conditions and Flight Delays")

# Explain data source
st.markdown("""
Data Source: [National Centers for Environmental Information (NCEI)](https://www.ncei.noaa.gov/)
""")

# Sidebar parameter settings
with st.sidebar:
    st.header("Query Parameters")
    
    # Set default dates (last 30 days)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    
    # 日期选择
    start_date = st.date_input("开始日期", start_date)
    end_date = st.date_input("结束日期", end_date)
    
    # Weather station selection (airport weather stations)
    st.markdown("### Airport Weather Station ID")
    col1, col2 = st.columns(2)
    with col1:
        station = st.text_input("Primary Weather Station", "USW00094846", 
                              help="e.g., USW00094846 (Chicago O'Hare Airport)")
    with col2:
        compare_station = st.text_input("Comparison Weather Station (Optional)", "",
                                      help="Enter another station ID for comparison")
    
    # Unit selection
    units = st.radio("Unit System", ["metric", "standard"], index=0)
    
    # Weather variable selection
    st.markdown("### Weather Variables")
    basic_vars = st.multiselect(
        "Basic Variables",
        ["TMAX", "TMIN", "TAVG", "PRCP"],
        ["TMAX", "TMIN"],
        help="Basic weather data such as temperature and precipitation"
    )
    
    aviation_vars = st.multiselect(
        "Aviation-Related Variables",
        ["AWND", "WSF2", "WSF5", "RH", "VIS", "GUST", "SNOW", "WT01"],
        ["AWND", "VIS", "RH"],
        help="""
        AWND: Average wind speed, WSF2: Maximum wind speed (2 minutes), WSF5: Maximum wind speed (5 minutes)
        RH: Relative humidity, VIS: Visibility, GUST: Gust, SNOW: Snowfall, WT01: Fog
        """
    )
    
    # Submit button
    submit_button = st.button("Fetch Weather Data")

# Build API request URL
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

# Fetch data
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return None

# Main interface
if submit_button:
    st.subheader(f"Weather Data Analysis from {start_date} to {end_date}")
    
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
        st.success(f"Successfully fetched {len(df)} records")
        
        # 合并对比数据
        if compare_station and df_compare is not None and not df_compare.empty:
            df = pd.concat([df, df_compare])
            st.success(f"Successfully fetched comparison station {len(df_compare)} records")
        
        # Display station information
        if 'STATION' in df.columns and 'NAME' in df.columns:
            st.markdown("### Weather Station Information")
            cols = st.columns(3)
            with cols[0]:
                st.metric("Station ID", df['STATION'].iloc[0])
            with cols[1]:
                st.metric("Station Name", df['NAME'].iloc[0])
            with cols[2]:
                st.metric("Location", f"{df['LATITUDE'].iloc[0]}, {df['LONGITUDE'].iloc[0]}")
        
        # Data preprocessing
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # Convert unit labels
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
        
        # Convert numeric columns
        numeric_cols = all_vars + ['LATITUDE', 'LONGITUDE']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["Temperature Analysis", "Aviation Weather Analysis", "Raw Data"])
        
        with tab1:
            # 温度数据可视化
            temp_cols = [col for col in ['TMAX', 'TMIN', 'TAVG'] if col in df.columns]
            if temp_cols:
                fig_temp = px.line(df, x='DATE', y=temp_cols,
                                 color='STATION' if compare_station else None,
                                 title='Daily Temperature Changes',
                                 labels={'value': f'Temperature ({unit_labels["TMAX"]})', 'DATE': 'Date'},
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
                               title='Temperature Distribution Statistics',
                               labels={'value': f'Temperature ({unit_labels["TMAX"]})'})
                st.plotly_chart(fig_box, use_container_width=True)
        
        with tab2:
            # 风速分析
            wind_cols = [col for col in ['AWND', 'WSF2', 'WSF5', 'GUST'] if col in df.columns]
            if wind_cols:
                st.markdown("### Wind Speed Analysis")
                fig_wind = px.line(df, x='DATE', y=wind_cols,
                                  color='STATION' if compare_station else None,
                                  title='Wind Speed Changes',
                                  labels={'value': f'Wind Speed ({unit_labels["AWND"]})', 'DATE': 'Date'})
                st.plotly_chart(fig_wind, use_container_width=True)
                
                # 风速玫瑰图
                if 'AWND' in df.columns and 'LATITUDE' in df.columns:
                    st.markdown("#### Wind Direction Frequency Analysis")
                    if 'WDF2' in df.columns:  # 风向数据
                        fig_windrose = px.bar_polar(df, r='AWND', theta='WDF2',
                                                   color='STATION' if compare_station else None,
                                                   title='Wind Speed and Direction Rose Chart',
                                                   labels={'r': f'Wind Speed ({unit_labels["AWND"]})'})
                        st.plotly_chart(fig_windrose, use_container_width=True)
                    else:
                        st.warning("No wind direction data (WDF2) available")
            
            # 能见度分析
            if 'VIS' in df.columns:
                st.markdown("### Visibility Analysis")
                fig_vis = px.line(df, x='DATE', y='VIS',
                                color='STATION' if compare_station else None,
                                title='Visibility Changes',
                                labels={'VIS': f'Visibility ({unit_labels["VIS"]})', 'DATE': 'Date'})
                st.plotly_chart(fig_vis, use_container_width=True)
            
            # 湿度分析
            if 'RH' in df.columns:
                st.markdown("### Relative Humidity Analysis")
                fig_rh = px.line(df, x='DATE', y='RH',
                               color='STATION' if compare_station else None,
                               title='Relative Humidity Changes',
                               labels={'RH': 'Relative Humidity (%)', 'DATE': 'Date'})
                st.plotly_chart(fig_rh, use_container_width=True)
            
            # 天气现象分析
            weather_codes = [col for col in df.columns if col.startswith('WT')]
            if weather_codes:
                st.markdown("### Adverse Weather Phenomena")
                weather_df = df[['DATE', 'STATION'] + weather_codes].melt(
                    id_vars=['DATE', 'STATION'], var_name='Weather Phenomenon', value_name='Occurrence')
                weather_df = weather_df[weather_df['Occurrence'] == 1]
                
                if not weather_df.empty:
                    fig_weather = px.histogram(weather_df, x='DATE', color='Weather Phenomenon',
                                             facet_row='STATION' if compare_station else None,
                                             title='Occurrences of Adverse Weather Phenomena',
                                             labels={'count': 'Occurrences'})
                    st.plotly_chart(fig_weather, use_container_width=True)
                else:
                    st.info("No adverse weather phenomena recorded during the query period")
        
        with tab3:
            # Display raw data
            st.dataframe(df)
            
            # Data download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name=f"weather_data_{start_date}_{end_date}.csv",
                mime='text/csv'
            )
    
    elif df is not None and df.empty:
        st.warning("No data found matching the criteria")
    else:
        st.error("Unable to fetch data, please check the parameters or try again later")

else:
    st.info("Please set query parameters in the sidebar and click 'Fetch Weather Data'")
    st.markdown("""
    ### Common Airport Weather Station IDs:
    | Airport | Station ID |
    |---------|------------|
    | Atlanta Hartsfield | USW00013874 |
    | Chicago O'Hare | USW00094846 |
    | Dallas/Fort Worth | USW00013960 |
    | Denver International | USW00003017 |
    | Los Angeles International | USW00023174 |
    | New York Kennedy | USW00094789 |
    | San Francisco International | USW00023234 |
    | Seattle-Tacoma | USW00024233 |
    
    More stations can be found via [NCEI Station Search](https://www.ncei.noaa.gov/access/search/)
    """)
