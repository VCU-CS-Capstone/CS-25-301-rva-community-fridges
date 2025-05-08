# components/map_view.py

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import plotly.express as px
import time
from datetime import datetime, timedelta

from utils.aws import get_latest_data_for_all_fridges
from utils.data import get_all_fridge_coordinates, get_fridge_locations, determine_fridge_status
from utils.helpers import safe_plotly_chart
from styles.custom_css import apply_custom_css, color_status_style, get_status_color_map

import config

def show_map_view():
    # ─── 1) one-time setup ────────────────────────────────────
    apply_custom_css()
    st.title("Community Fridge Locations")
    
    # Initialize auto-refresh state if it doesn't exist
    if "map_auto_refresh_enabled" not in st.session_state:
        st.session_state.map_auto_refresh_enabled = False

    # Move refresh control button to sidebar to be consistent with dashboard
    st.sidebar.empty()  # Add a little spacing
    if st.sidebar.button(
        "Stop Auto-Refresh" if st.session_state.map_auto_refresh_enabled else "Start Auto-Refresh",
        key="map_refresh_toggle"
    ):
        st.session_state.map_auto_refresh_enabled = not st.session_state.map_auto_refresh_enabled
    
    # filter widget created once
    ALL_STATUSES = ["Normal", "Too cold", "Too warm", "No data"]
    status_filter = st.multiselect(
        "Filter by Status",
        options=ALL_STATUSES,
        default=ALL_STATUSES,
        key="map_status_filter"
    )

    # build the base map once - keep this outside the refresh loop
    coords     = get_all_fridge_coordinates()
    latest_all = get_latest_data_for_all_fridges()
    base_map   = folium.Map(location=[37.5407, -77.4360], zoom_start=12)
    cluster    = MarkerCluster().add_to(base_map)

    for fid, addr in get_fridge_locations().items():
        if fid not in coords:
            continue
        lat, lon = coords[fid]
        data = latest_all.get(fid, {})
        temp = data.get("temp")
        status, color = (
            determine_fridge_status(float(temp)) if temp is not None
            else ("No data", "gray")
        )
        folium.Marker(
            [lat, lon],
            popup=(
                f"<b>{fid}</b><br>{addr}"
                f"<br><b>Status:</b> {status}"
                f"<br><b>Temp:</b> {temp if temp is not None else 'N/A'}°C"
            ),
            icon=folium.Icon(color=color, icon="snowflake", prefix="fa")
        ).add_to(cluster)

    st.subheader("Interactive Map")
    folium_static(base_map, width=800, height=400)

    # ─── Create placeholder for dynamic content ─────────────────────
    data_container = st.empty()
    refresh_footer = st.empty()

    # Function to update data content
    def update_data_content():
        # fetch fresh data
        latest_all = get_latest_data_for_all_fridges()
        rows = []
        for fid, addr in get_fridge_locations().items():
            if fid not in coords:
                continue
            data = latest_all.get(fid, {})
            temp = data.get("temp")
            if temp is not None:
                status, _ = determine_fridge_status(float(temp))
                door    = data.get("door_usage", "N/A")
                updated = data.get("est_time",    "N/A")
            else:
                status, door, updated = "No data", "N/A", "N/A"

            rows.append({
                "Fridge ID":         fid,
                "Address":           addr,
                "Status":            status,
                "Temperature (°F)":  temp if temp is not None else "N/A",
                "Door Usage (24h)":  door,
                "Last Updated":      updated
            })

        df = pd.DataFrame(rows)
        filtered = df[df["Status"].isin(status_filter)]

        with data_container.container():
            # table + pie in two columns
            col_table, col_chart = st.columns([4,2])

            with col_table:
                st.subheader("Fridge Status Table")
                st.caption(f"Showing {len(filtered)} of {len(df)} fridges")
                styled = filtered.style.map(
                    color_status_style(), subset=["Status"]
                )
                
                # Add column width configuration
                st.dataframe(
                    styled, 
                    hide_index=True, 
                    use_container_width=True,
                    column_config={
                        "Last Updated": st.column_config.TextColumn(width=200),
                        "Fridge ID": st.column_config.TextColumn(width=150),
                        "Address": st.column_config.TextColumn(width=250),
                        "Status": st.column_config.TextColumn(width=100),
                        "Temperature (°F)": st.column_config.TextColumn(width=120),
                        "Door Usage (24h)": st.column_config.TextColumn(width=120)
                    }
                )

            with col_chart:
                st.subheader("Status Distribution")
                counts = filtered["Status"].value_counts()
                if not counts.empty:
                    fig = px.pie(
                        names=counts.index,
                        values=counts.values,
                        color=counts.index,
                        color_discrete_map=get_status_color_map()
                    )
                    safe_plotly_chart(fig, prefix="map_status_pie")
                else:
                    st.info("No statuses to show.")

            st.caption(f"Last refreshed: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # Initial data load
    update_data_content()
    
    # Show appropriate footer message
    if not st.session_state.map_auto_refresh_enabled:
        refresh_footer.caption("Auto-refresh is disabled. Click 'Start Auto-Refresh' in the sidebar to enable.")
    
    # ─── Auto-refresh loop ────────────────────────────────────
    while st.session_state.map_auto_refresh_enabled:
        next_refresh_time = datetime.now() + timedelta(seconds=config.REFRESH_RATE)
        refresh_footer.caption(f"Auto-refresh enabled. Next update @ {next_refresh_time.strftime('%H:%M:%S')}")
        
        time.sleep(config.REFRESH_RATE)
        update_data_content()