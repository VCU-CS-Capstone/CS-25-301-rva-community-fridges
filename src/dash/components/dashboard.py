import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import time
import plotly.express as px

import config
from utils.aws import get_latest_data_for_fridge, get_historical_data_for_fridge
from utils.data import determine_fridge_status, get_all_fridge_coordinates
from utils.helpers import create_tooltip, safe_plotly_chart
from components.tooltips import create_dashboard_guides

def show_dashboard():
    # ─── Sidebar ─────────────────────────────────────────────
    fridge_selection = st.sidebar.selectbox(
        "Select Fridge",
        options=list(config.FRIDGE_OPTIONS.keys()),
        format_func=lambda x: f"{x}: {config.FRIDGE_OPTIONS[x]}",
        key="dashboard_fridge_select"
    )
    fridge_id = config.FRIDGE_OPTIONS[fridge_selection]
    st.sidebar.info(f"Fridge ID: {fridge_id}")

    time_range = st.sidebar.selectbox(
        "Select Time Range",
        ["Last Hour", "Last 24 Hours", "Last 7 Days"],
        key="dashboard_time_range"
    )

    # Initialize auto-refresh state if it doesn't exist
    if "auto_refresh_enabled" not in st.session_state:
        st.session_state.auto_refresh_enabled = False

    # Add refresh control button to sidebar
    if st.sidebar.button(
        "Stop Auto-Refresh" if st.session_state.auto_refresh_enabled else "Start Auto-Refresh",
        key="refresh_toggle"
    ):
        st.session_state.auto_refresh_enabled = not st.session_state.auto_refresh_enabled

    # ─── Title & Guide ───────────────────────────────────────
    st.title("Fridge Monitoring Dashboard")
    if st.session_state.get("show_tips", False):
        create_dashboard_guides()

    # ─── Static Mini-Map (renders once) ──────────────────────
    coords = get_all_fridge_coordinates()
    if fridge_id in coords:
        lat, lon = coords[fridge_id]
        map_box = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker(
            [lat, lon],
            popup=f"{fridge_id}",
            tooltip=fridge_id,
            icon=folium.Icon(color="blue", icon="snowflake", prefix="fa")
        ).add_to(map_box)
        folium_static(map_box, width=700, height=300)

    # ─── Create placeholder slots for dynamic content ─────────
    status_slot = st.empty()  # Use empty() not container()
    history_slot = st.empty()  # Use empty() not container()
    footer_slot = st.empty()

    # Function to update the content
    def update_content():
        now = datetime.now()
        if time_range == "Last Hour":
            start_dt = now - timedelta(hours=1)
        elif time_range == "Last 24 Hours":
            start_dt = now - timedelta(days=1)
        else:
            start_dt = now - timedelta(days=7)
        
        # Update status display
        with status_slot.container():
            latest = get_latest_data_for_fridge(fridge_id)
            if not latest:
                st.warning("No recent data.")
            else:
                # parse
                temp_val = float(latest.get("temp")) if latest.get("temp") else None
                door_val = latest.get("door_usage", "N/A")
                updated  = latest.get("est_time", "N/A")

                # determine status
                status_text, color = (
                    determine_fridge_status(temp_val)
                    if temp_val is not None else ("Unknown", "gray")
                )

                # three columns: Temp / Door / Status pill
                col_t, col_d, col_s = st.columns([1,1,1])
                col_t.metric("🌡️ Temperature", f"{temp_val:.1f}°F" if temp_val is not None else "N/A")
                col_d.metric("🚪 Door Usage (24h)", door_val)

                # status pill
                col_s.markdown(
                    f"""
                    <div style="
                      background:{color};
                      padding:8px;
                      border-radius:4px;
                      color:white;
                      text-align:center;
                      font-weight:bold;
                    ">{status_text}</div>
                    """,
                    unsafe_allow_html=True
                )

                # small footer under those columns
                st.caption(f"Last updated: {updated}")
        
        # Update history display
        with history_slot.container():
            st.subheader("Historical Data")
            hist = get_historical_data_for_fridge(fridge_id, start_dt, now)
            if hist.empty:
                st.info("No history in this range.")
            else:
                hist["temp"] = pd.to_numeric(hist["temp"], errors="coerce")
                hist["door_usage"] = pd.to_numeric(hist["door_usage"], errors="coerce")

                hist.sort_values('est_time_dt')

                tabs = st.tabs(["Temp", "Doors", "Stats"])
                with tabs[0]:
                    fig = px.line(hist, x="est_time_dt", y="temp", title="Temperature")
                    safe_plotly_chart(fig, prefix="hist_temp")
                with tabs[1]:
                    fig = px.scatter(hist, x="est_time_dt", y="door_usage", title="Door Usage")
                    safe_plotly_chart(fig, prefix="hist_door")
                with tabs[2]:
                    t = hist["temp"]; d = hist["door_usage"]
                    a, b, c = st.columns(3)
                    a.metric("Avg Temp", f"{t.mean():.1f}°F")
                    b.metric("Max Temp", f"{t.max():.1f}°F")
                    c.metric("Min Temp", f"{t.min():.1f}°F")
                    x, y, z = st.columns(3)
                    x.metric("Σ Door Interaction", int(d.sum()))
                    y.metric("Max Door Interaction", int(d.max()))
                    z.metric("Avg Door Interaction", f"{d.mean():.1f}")

    # Initial content load
    update_content()
    
    # Show appropriate footer message
    if not st.session_state.auto_refresh_enabled:
        footer_slot.caption("Auto-refresh is disabled. Click 'Start Auto-Refresh' in the sidebar to enable.")

    # Refresh loop
    while st.session_state.auto_refresh_enabled:
        now = datetime.now()
        next_refresh = now + timedelta(seconds=config.REFRESH_RATE)
        footer_slot.caption(f"Auto-refresh enabled. Next update @ {next_refresh.strftime('%H:%M:%S')}")
        
        time.sleep(config.REFRESH_RATE)
        update_content()