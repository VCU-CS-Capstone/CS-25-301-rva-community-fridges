import streamlit as st
import pandas as pd
import plotly.express as px
import boto3
from datetime import datetime, timedelta
import time
import requests
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Page configuration
st.set_page_config(
    page_title="Fridge Monitoring Dashboard",
    page_icon="🧊",
    layout="wide"
)

# Load AWS credentials from environment variables or config
import os
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

# Sidebar for configuration
st.sidebar.title("Fridge Monitoring Dashboard")

# AWS configuration
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "us-east-1")

# Timestream database and table configuration
database_name = os.getenv("TIMESTREAM_DATABASE", "RVACF-Timestream-DB")
table_name = os.getenv("TIMESTREAM_TABLE", "multi_value")

# Define fridge options and locations
fridge_options = {
    0: "venable-st-fridge",
    1: "hull-st-fridge",
    2: "new-kingdom-fridge",
    3: "oakwood-art-fridge",
    4: "city-church-fridge",
    5: "studio-23-fridge",
    6: "fulton-hill-fridge",
    7: "cary-st-fridge",
    8: "sankofa-fridge",
    9: "meadowbridge-fridge",
    10: "6pic-fridge",
    11: "fonticello-fridge",
    12: "matchbox-mutualaid",
    13: "main-st-fridge"
}

fridge_locations = {
    'venable-st-fridge': '2025 Venable St, Richmond, VA',
    'new-kingdom-fridge': '3200 Dill Ave, Richmond, VA',
    'studio-23-fridge': '109 W 15th St, Richmond, VA',
    'hull-st-fridge': '2414 Hull St, Richmond, VA',
    'matchbox-mutualaid': '2919 North Ave, Richmond, VA',
    '6pic-fridge': '3001 Meadowbridge Rd, Virginia',
    'meadowbridge-fridge': '3613 Meadowbridge Rd, Richmond, VA',
    'fonticello-fridge': '255 W 27th St, Richmond, VA',
    'fulton-hill-fridge': '4809 Parker St, Richmond, VA',
    'city-church-fridge': '4700 Oakleys Ln, Richmond, VA',
    'sankofa-fridge': '309 Covington Rd, Richmond, VA',
    'oakwood-art-fridge': '917 N 35th St, Richmond, VA',
    'cary-st-fridge': '2913 W Cary St, Richmond, VA',
    'main-st-fridge': '121 E Main St, Richmond, VA'
}

fridge_coordinates = {
    'venable-st-fridge': (37.5395, -77.4259),
    'new-kingdom-fridge': (37.5601, -77.4368),
    'studio-23-fridge': (37.5360, -77.4338),
    'hull-st-fridge': (37.5358, -77.4478),
    'matchbox-mutualaid': (37.5807, -77.4255),
    '6pic-fridge': (37.5756, -77.4219),
    'meadowbridge-fridge': (37.5870, -77.4215),
    'fonticello-fridge': (37.5316, -77.4330),
    'fulton-hill-fridge': (37.5299, -77.4048),
    'city-church-fridge': (37.5238, -77.3477),
    'sankofa-fridge': (37.5659, -77.4666),
    'oakwood-art-fridge': (37.5409, -77.4113),
    'cary-st-fridge': (37.5553, -77.4834),
    'main-st-fridge': (37.5350, -77.4396)
}

# Function to get fridge coordinates
def get_all_fridge_coordinates():
    return fridge_coordinates

# Function to connect to AWS Timestream and execute queries
@st.cache_data(ttl=300)
def query_timestream(query, aws_access_key, aws_secret_key, region):
    if not aws_access_key or not aws_secret_key:
        st.warning("AWS credentials not found. Using demo data.")
        return None
        
    client = boto3.client(
        'timestream-query',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )
    
    try:
        response = client.query(QueryString=query)
        return response
    except Exception as e:
        st.error(f"Error querying Timestream: {str(e)}")
        return None

# Function to parse Timestream query results into pandas DataFrame
def parse_query_result(result):
    if not result:
        return pd.DataFrame()
        
    columns = [col['Name'] for col in result['ColumnInfo']]
    data = []
    
    for row in result['Rows']:
        parsed_row = []
        for cell in row['Data']:
            if 'ScalarValue' in cell:
                parsed_row.append(cell['ScalarValue'])
            elif 'NullValue' in cell:
                parsed_row.append(None)
            else:
                parsed_row.append(str(cell))
        
        data.append(parsed_row)
    
    return pd.DataFrame(data, columns=columns)

# Function to get latest data for all fridges
@st.cache_data(ttl=60)  # Cache for 1 minute
def get_latest_data_for_all_fridges():
    # Query to get latest data for all fridges
    query = f"""
    SELECT fridge_id, est_time, temp, door_usage
    FROM "{database_name}"."{table_name}"
    WHERE time > ago(24h)
    ORDER BY est_time DESC
    """
    
    result = query_timestream(query, aws_access_key, aws_secret_key, aws_region)
    df = parse_query_result(result)
    
    if df.empty:
        return pd.DataFrame()
    
    # Get latest data for each fridge
    latest_data = {}
    
    if not df.empty and 'fridge_id' in df.columns:
        for fridge_id in fridge_options.values():
            fridge_data = df[df['fridge_id'] == fridge_id]
            if not fridge_data.empty:
                latest_data[fridge_id] = fridge_data.iloc[0].to_dict()
    
    return latest_data

# Function to get latest data for a specific fridge
@st.cache_data(ttl=60)  # Cache for 1 minute
def get_latest_data_for_fridge(fridge_id):
    query = f"""
    SELECT fridge_id, est_time, temp, door_usage
    FROM "{database_name}"."{table_name}"
    WHERE fridge_id = '{fridge_id}'
    ORDER BY est_time DESC
    LIMIT 1
    """
    
    result = query_timestream(query, aws_access_key, aws_secret_key, aws_region)
    df = parse_query_result(result)
    
    if df.empty:
        return None
    
    return df.iloc[0].to_dict()

# Function to get historical data for a specific fridge
@st.cache_data(ttl=300)
def get_historical_data_for_fridge(fridge_id, measure_column, start_datetime, end_datetime, use_aggregation=False, aggregation="AVG", time_bin="1h"):
    # Format timestamps for est_time comparison
    # Use MM/DD/YYYY, HH:MM:SS AM/PM format for est_time string comparison
    start_time_str = start_datetime.strftime('%m/%d/%Y, %I:%M:%S %p')
    end_time_str = end_datetime.strftime('%m/%d/%Y, %I:%M:%S %p')
    
    if use_aggregation:
        time_bin_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "1d": "1d"
        }
        
        bin_size = time_bin_map[time_bin]
        
        # For aggregated queries, we need to use the time column with bin
        query = f"""
        SELECT 
            SUBSTRING(est_time, 1, 10) AS date,
            bin(time, {bin_size}) AS binned_time,
            {aggregation}({measure_column}) AS {measure_column}_{aggregation.lower()},
            fridge_id
        FROM 
            "{database_name}"."{table_name}"
        WHERE 
            fridge_id = '{fridge_id}'
            AND parse_datetime(est_time, 'MM/dd/yyyy, hh:mm:ss a') 
                BETWEEN parse_datetime('{start_time_str}', 'MM/dd/yyyy, hh:mm:ss a') 
                AND parse_datetime('{end_time_str}', 'MM/dd/yyyy, hh:mm:ss a')
        GROUP BY 
            SUBSTRING(est_time, 1, 10), bin(time, {bin_size}), fridge_id
        ORDER BY 
            binned_time DESC
        """
    else:
        # For regular queries, directly use est_time
        query = f"""
        SELECT est_time, {measure_column}, fridge_id, region, time
        FROM "{database_name}"."{table_name}"
        WHERE fridge_id = '{fridge_id}'
        AND parse_datetime(est_time, 'MM/dd/yyyy, hh:mm:ss a') 
            BETWEEN parse_datetime('{start_time_str}', 'MM/dd/yyyy, hh:mm:ss a') 
            AND parse_datetime('{end_time_str}', 'MM/dd/yyyy, hh:mm:ss a')
        ORDER BY est_time DESC
        """
    
    result = query_timestream(query, aws_access_key, aws_secret_key, aws_region)
    df = parse_query_result(result)
    
    if df.empty:
        return pd.DataFrame()
    
    # Process data for visualization
    if not use_aggregation and 'est_time' in df.columns:
        # Keep original est_time for display
        df['display_time'] = df['est_time']
        # Create a datetime column for plotting
        df['est_time_dt'] = pd.to_datetime(df['est_time'], format='%m/%d/%Y, %I:%M:%S %p')
    elif use_aggregation and 'binned_time' in df.columns:
        # For aggregated data, use binned_time
        df['binned_time'] = pd.to_datetime(df['binned_time'])
    
    return df

# Function to determine fridge status
def determine_fridge_status(temp):
    if temp is None:
        return "Unknown", "gray"
    
    temp = float(temp)
    if 2 <= temp <= 6:
        return "Operating normally", "green"
    elif temp < 2:
        return "Too cold", "blue"
    else:  # temp > 6
        return "Too warm", "red"

# Generate demo data for a fridge based on fridge_id
def get_demo_data(fridge_id):
    import random
    
    # Use hash of fridge_id to generate consistent values
    hash_val = hash(fridge_id) % 100
    
    # Temperature between 2-8°C with some outliers
    if hash_val < 70:  # 70% normal
        temp = round(random.uniform(2, 6), 1)
        status = "Operating normally"
        color = "green"
    elif hash_val < 85:  # 15% too cold
        temp = round(random.uniform(0, 1.9), 1)
        status = "Too cold"
        color = "blue"
    else:  # 15% too warm
        temp = round(random.uniform(6.1, 8), 1)
        status = "Too warm"
        color = "red"
        
    door_usage = int(50 + hash_val * 2.5)
    
    # Generate timestamp
    current_time = datetime.now()
    est_time = current_time.strftime('%m/%d/%Y, %I:%M:%S %p')
    
    return {
        "fridge_id": fridge_id,
        "est_time": est_time,
        "temp": temp,
        "door_usage": door_usage,
        "status": status,
        "color": color
    }

# Main navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Map View"])

# Check for AWS credentials
has_credentials = aws_access_key and aws_secret_key
if has_credentials:
    st.sidebar.success("✅ AWS Credentials Configured")
else:
    st.sidebar.warning("⚠️ AWS Credentials Not Found - Using Demo Data")

# Toggle for demo mode
use_demo_data = st.sidebar.checkbox("Force Demo Mode", value=not has_credentials)

if page == "Dashboard":
    # Define query options
    st.sidebar.title("Fridge Selection")
    # Create a dropdown for fridge selection
    fridge_selection = st.sidebar.selectbox(
        "Select Fridge",
        options=list(fridge_options.keys()),
        format_func=lambda x: f"{x}: {fridge_options[x]}"
    )
    fridge_id = fridge_options[fridge_selection]

    # Display selected fridge ID
    st.sidebar.info(f"Selected fridge ID: {fridge_id}")
    
    # Add dropdown for available metrics
    available_metrics = ["temp", "door_usage"]
    measure_column = st.sidebar.selectbox("Select Metric", available_metrics)

    # Time range selector for historical data
    st.sidebar.title("Historical Data")
    time_range = st.sidebar.selectbox(
        "Select Time Range",
        ["Last Hour", "Last 24 Hours", "Last 7 Days", "Custom"]
    )

    if time_range == "Custom":
        start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=1))
        end_date = st.sidebar.date_input("End Date", datetime.now())
        start_time = st.sidebar.time_input("Start Time", datetime.min.time())
        end_time = st.sidebar.time_input("End Time", datetime.max.time())
        
        start_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
    else:
        end_datetime = datetime.now()
        if time_range == "Last Hour":
            start_datetime = end_datetime - timedelta(hours=1)
        elif time_range == "Last 24 Hours":
            start_datetime = end_datetime - timedelta(days=1)
        else:  # Last 7 Days
            start_datetime = end_datetime - timedelta(days=7)

    # Optional aggregation settings
    use_aggregation = st.sidebar.checkbox("Use Aggregation")
    if use_aggregation:
        aggregation = st.sidebar.selectbox(
            "Aggregation Function",
            ["AVG", "MAX", "MIN", "SUM", "COUNT"]
        )
        time_bin = st.sidebar.selectbox(
            "Time Bin",
            ["1m", "5m", "15m", "1h", "1d"]
        )

    # Add fridge details to the dashboard header
    st.title(f"Fridge Monitoring Dashboard")
    
    # Create columns for header info and mini map
    header_col1, header_col2 = st.columns([3, 2])
    
    with header_col1:
        st.subheader(f"Selected Fridge: {fridge_id}")
        st.markdown(f"**Location**: {fridge_locations.get(fridge_id, 'Location not available')}")
    
    with header_col2:
        # Show a mini map of the selected fridge
        fridge_coords = get_all_fridge_coordinates()
        if fridge_id in fridge_coords:
            lat, lon = fridge_coords[fridge_id]
            mini_map = folium.Map(location=[lat, lon], zoom_start=15, width=400, height=200)
            folium.Marker(
                [lat, lon],
                popup=f"<b>{fridge_id}</b><br>{fridge_locations[fridge_id]}",
                tooltip=fridge_id,
                icon=folium.Icon(color="blue", icon="snowflake", prefix="fa")
            ).add_to(mini_map)
            folium_static(mini_map, width=400, height=200)
        else:
            st.warning("Location coordinates not available for this fridge")

    # Display latest data
    st.subheader("Current Status")
    
    # Get latest data for this fridge
    if use_demo_data:
        latest_data = get_demo_data(fridge_id)
    else:
        latest_data = get_latest_data_for_fridge(fridge_id)
        
        if latest_data is None:
            st.warning(f"No recent data available for {fridge_id}. Showing demo data instead.")
            latest_data = get_demo_data(fridge_id)
    
    # Display latest metrics in a nice layout
    if latest_data:
        # Determine status based on temperature
        if 'temp' in latest_data and latest_data['temp'] is not None:
            temp = float(latest_data['temp']) 
            status, color = determine_fridge_status(temp)
        else:
            temp = None
            status = "Unknown"
            color = "gray"
        
        # Get door usage
        door_usage = latest_data.get('door_usage', 'N/A')
        
        # Display timestamp
        est_time = latest_data.get('est_time', 'N/A')
        
        # Create a nice layout for current status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Temperature",
                value=f"{temp}°C" if temp is not None else "No data",
                delta=None
            )
            
        with col2:
            st.metric(
                label="Door Usage (24h)",
                value=door_usage if door_usage != 'N/A' else "No data",
                delta=None
            )
            
        with col3:
            # Create a colored status indicator
            st.markdown(f"""
            <div style="
                background-color: {color}; 
                padding: 10px; 
                border-radius: 5px; 
                color: white; 
                text-align: center;
                margin-top: 25px;
                font-weight: bold;
            ">
                {status}
            </div>
            """, unsafe_allow_html=True)
        
        st.caption(f"Last updated: {est_time}")
    else:
        st.error("No data available for this fridge.")
    
    # Get historical data
    st.subheader("Historical Data")
    
    # Show a loading indicator
    with st.spinner("Loading historical data..."):
        if use_demo_data:
            # Generate sample data for demo
            sample_dates = pd.date_range(
                start=start_datetime,
                end=end_datetime,
                freq='1H'
            )
            
            # Create sample est_time in the format shown in the data
            sample_est_times = [d.strftime('%m/%d/%Y, %I:%M:%S %p') for d in sample_dates]
            
            # Generate patterns based on fridge ID
            fridge_num = fridge_selection
            
            # Generate sample temperature data with patterns that vary by fridge
            base_temp = 3 + (fridge_num % 3)  # Base temperature varies by fridge (3-5°C)
            temp_variation = 1 + (fridge_num % 2)  # Temperature variation (1-2°C)
            
            # Generate sample door usage data
            door_base = 50 + (fridge_num * 10)  # Base door usage varies by fridge
            door_variation = 20 + (fridge_num % 5) * 10  # Door usage variation
            
            historical_data = pd.DataFrame({
                'est_time': sample_est_times,
                'est_time_dt': sample_dates,
                'temp': [
                    base_temp + temp_variation * (hour % 24 / 12) * (1 + 0.2 * (day + fridge_num) % 3) for 
                    day, hour in zip(
                        range(len(sample_dates)), 
                        [d.hour for d in sample_dates]
                    )
                ],
                'door_usage': [
                    door_base + door_variation * ((hour + 3) % 24 / 12) * (1 - 0.1 * (day + fridge_num) % 4) for 
                    day, hour in zip(
                        range(len(sample_dates)), 
                        [d.hour for d in sample_dates]
                    )
                ],
                'fridge_id': fridge_id,
                'region': 'us-east-1'
            })
            
            # Round numeric values to 1 decimal place
            historical_data['temp'] = historical_data['temp'].round(1)
            historical_data['door_usage'] = historical_data['door_usage'].round(1)
            
            time_col = 'est_time_dt'
            value_col = measure_column
            
        else:
            # Get real historical data
            historical_data = get_historical_data_for_fridge(
                fridge_id, 
                measure_column, 
                start_datetime, 
                end_datetime,
                use_aggregation
            )
            
            # Determine column names for plotting
            if historical_data.empty:
                st.warning(f"No historical data available for {fridge_id} in the selected time range.")
                # Skip the rest of the historical data section
                st.stop()
            else:
                # Determine column names for plotting
                if use_aggregation:
                    value_col = f"{measure_column}_{aggregation.lower()}"
                    time_col = 'binned_time'
                else:
                    value_col = measure_column
                    time_col = 'est_time_dt'
        
        # Display the historical data
        with st.expander("Show Raw Data"):
            st.dataframe(historical_data)
        
        # Create title for visualization
        title_prefix = f"Fridge {fridge_selection}: {fridge_id}"
        
        # Create visualization
        fig = px.line(
            historical_data, 
            x=time_col, 
            y=value_col,
            title=f"{title_prefix} - {measure_column} over time" if not use_aggregation else f"{title_prefix} - {aggregation} of {measure_column} over time",
            labels={time_col: "Time", value_col: measure_column if not use_aggregation else f"{aggregation} of {measure_column}"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                f"Average {measure_column}", 
                f"{pd.to_numeric(historical_data[value_col], errors='coerce').mean():.2f}"
            )
        
        with col2:
            st.metric(
                f"Max {measure_column}", 
                f"{pd.to_numeric(historical_data[value_col], errors='coerce').max():.2f}"
            )
            
        with col3:
            st.metric(
                f"Min {measure_column}", 
                f"{pd.to_numeric(historical_data[value_col], errors='coerce').min():.2f}"
            )

elif page == "Map View":
    st.title("Community Fridge Locations")
    
    # Automatically refresh data
    auto_refresh = st.checkbox("Auto-refresh (every minute)", value=True)
    
    if auto_refresh:
        refresh_interval = 60  # 60 seconds
        refresh_placeholder = st.empty()
        refresh_time = datetime.now() + timedelta(seconds=refresh_interval)
        refresh_placeholder.info(f"Next refresh in {refresh_interval} seconds (at {refresh_time.strftime('%H:%M:%S')})")
    
    # Get all fridge coordinates
    fridge_coords = get_all_fridge_coordinates()
    
    # Create a map centered on Richmond, VA
    m = folium.Map(location=[37.5407, -77.4360], zoom_start=12)
    
    # Create a marker cluster for better visualization
    marker_cluster = MarkerCluster().add_to(m)
    
    # Get latest data for all fridges
    if use_demo_data:
        # Generate demo data for all fridges
        latest_data_all = {fridge_id: get_demo_data(fridge_id) for fridge_id in fridge_options.values()}
    else:
        # Get real data
        latest_data_all = get_latest_data_for_all_fridges()
        
        # Fill in missing fridges with demo data
        for fridge_id in fridge_options.values():
            if fridge_id not in latest_data_all:
                st.info(f"No data available for {fridge_id}. Using demo data.")
                latest_data_all[fridge_id] = get_demo_data(fridge_id)
    
    # Prepare data for table display
    fridge_table_data = []
    
    # Add markers for each fridge
    for fridge_id, address in fridge_locations.items():
        if fridge_id in fridge_coords:
            lat, lon = fridge_coords[fridge_id]
            
            # Get status data for this fridge
            if fridge_id in latest_data_all:
                fridge_data = latest_data_all[fridge_id]
                
                if 'temp' in fridge_data and fridge_data['temp'] is not None:
                    # Determine status based on temperature
                    status, color = determine_fridge_status(fridge_data['temp'])
                    temp = float(fridge_data['temp'])
                    door_usage = fridge_data.get('door_usage', 'N/A')
                    last_updated = fridge_data.get('est_time', 'N/A')
                else:
                    status = "No data"
                    color = "gray"
                    temp = "N/A"
                    door_usage = "N/A"
                    last_updated = "N/A"
            else:
                status = "No data"
                color = "gray"
                temp = "N/A"
                door_usage = "N/A"
                last_updated = "N/A"
            
            # Create detailed popup with status info
            popup_html = f"""
            <div style="width: 200px">
                <h4>{fridge_id}</h4>
                <p><b>Address:</b> {address}</p>
                <p><b>Status:</b> {status}</p>
                <p><b>Temperature:</b> {temp if temp != 'N/A' else 'No data'}°C</p>
                <p><b>Door Usage (24h):</b> {door_usage}</p>
                <p><b>Last updated:</b> {last_updated}</p>
                <a href="/?page=Dashboard&fridge_id={fridge_id}" target="_blank">View Details</a>
            </div>
            """
            
            # Create marker with icon
            marker = folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=fridge_id,
                icon=folium.Icon(color=color, icon="snowflake", prefix="fa")
            )
            
            # Add marker to cluster
            marker.add_to(marker_cluster)
            
            # Add data for table
            fridge_table_data.append({
                "Fridge ID": fridge_id,
                "Address": address,
                "Status": status,
                "Temperature (°C)": temp if temp != 'N/A' else "No data",
                "Door Usage (24h)": door_usage,
                "Last Updated": last_updated
            })
    
    # Display the map
    st.subheader("Interactive Map of All Community Fridges")
    folium_static(m, width=1000, height=600)
    
    # Create a table with fridge information
    st.subheader("Fridge Status Information")
    
    # Convert to dataframe and display
    fridge_df = pd.DataFrame(fridge_table_data)
    
    # Add status coloring
    def color_status(val):
        if "normally" in val:
            return 'background-color: #c6efce; color: #006100'
        elif "cold" in val:
            return 'background-color: #bdd7ee; color: #1f497d'
        elif "warm" in val:
            return 'background-color: #ffc7ce; color: #9c0006'
        else:  # No data
            return 'background-color: #f2f2f2; color: #666666'
    
    # Display styled dataframe
    st.dataframe(fridge_df.style.applymap(color_status, subset=['Status']))
    
    # Add filtering options
    st.subheader("Filter Fridges")
    status_filter = st.multiselect(
        "Filter by Status",
        ["Operating normally", "Too cold", "Too warm", "No data"],
        default=["Operating normally", "Too cold", "Too warm", "No data"]
    )
    
    filtered_df = fridge_df[fridge_df['Status'].isin(status_filter)]
    st.write(f"Showing {len(filtered_df)} fridges")
    st.dataframe(filtered_df.style.applymap(color_status, subset=['Status']))
    
    # Add summary statistics
    st.subheader("Status Summary")
    status_counts = fridge_df['Status'].value_counts()
    fig = px.pie(
        status_counts, 
        values=status_counts.values, 
        names=status_counts.index,
        title="Fridge Status Distribution",
        color=status_counts.index,
        color_discrete_map={
            "Operating normally": "#c6efce", 
            "Too cold": "#bdd7ee", 
            "Too warm": "#ffc7ce",
            "No data": "#f2f2f2"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Streamlit AWS Timestream Fridge Monitoring Dashboard")

# Add timestamp for last refresh
st.sidebar.caption(f"Last refreshed: {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}")
