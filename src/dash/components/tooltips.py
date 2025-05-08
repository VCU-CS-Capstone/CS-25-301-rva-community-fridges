import streamlit as st

# Initialize session state for controlling tooltips
def initialize_tooltip_state():
    if 'show_tips' not in st.session_state:
        st.session_state.show_tips = True

# Helper function to create tooltips
def create_tooltip(text, tip_text):
    return f"""
    <div class="tooltip">{text} ⓘ
        <span class="tooltiptext">{tip_text}</span>
    </div>
    """

# Function to create guide cards
def create_guide_card(title, content):
    if st.session_state.show_tips:
        st.markdown(f"""
        <div class="guide-card">
            <h4>{title}</h4>
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)

# Function to create feature highlights
def create_feature_highlight(title, content, color="#2196F3"):
    if st.session_state.show_tips:
        st.markdown(f"""
        <div style="border: 1px dashed {color}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <p><strong>{title}</strong> {content}</p>
        </div>
        """, unsafe_allow_html=True)

# Function to add a tips toggle to the sidebar
def add_tips_toggle():
    tips_enabled = st.sidebar.checkbox("Show Helper Tips", value=st.session_state.show_tips, key="tips_toggle")
    if tips_enabled != st.session_state.show_tips:
        st.session_state.show_tips = tips_enabled
    return st.session_state.show_tips

# Function to add a help section to the sidebar
def add_help_section():
    with st.sidebar.expander("❓ Need Help?"):
        st.markdown("""
        ### Dashboard Controls
        - **Navigation:** Switch between Dashboard and Map View
        - **Fridge Selection:** Choose which fridge to monitor
        - **Time Range:** Select data time period
        - **Auto-Refresh:** Click Once to Start, Triple Click to Stop
        
        ### Status Colors
        - 🟢 **Green:** Operating normally (2-6°C)
        - 🔵 **Blue:** Too cold (below 2°C)
        - 🔴 **Red:** Too warm (above 6°C)
        - ⚪ **Gray:** No data available
        
        ### Contact
        For technical support, please contact:
        [support@fridgemonitoring.org](mailto:support@fridgemonitoring.org)
        """)

# Function to add keyboard shortcuts helper
def add_keyboard_shortcuts():
    with st.sidebar.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        - **R** - Manually refresh data
        - **F** - Toggle fullscreen
        - **S** - Save current view
        - **D** - Toggle dark/light mode
        """)

# Map guide card specific for map view
def create_map_guides():
    if st.session_state.show_tips:
        st.markdown("""
        <div class="guide-card">
            <h4>🔍 Map View Guide</h4>
            <p>Marker colors: <span style="color: green">●</span> Operating normally, 
            <span style="color: blue">●</span> Too cold, 
            <span style="color: red">●</span> Too warm, 
            <span style="color: gray">●</span> No data</p>
        </div>
        """, unsafe_allow_html=True)

# Map interaction tip
def create_map_interaction_tip():
    if st.session_state.show_tips:
        st.markdown("""
        <div style="border: 1px dashed #FF9800; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <p><strong>🖱️ Map Interaction Tips:</strong> 
            • Click on markers to see fridge details<br>
            • Zoom in/out with scroll wheel<br>
            • Click and drag to pan the map<br>
            • Click a marker's "View Details" link to see full dashboard for that fridge</p>
        </div>
        """, unsafe_allow_html=True)

# Dashboard guide card
def create_dashboard_guides():
    if st.session_state.show_tips:
        st.markdown("""
        <div class="guide-card">
            <h4>🔍 Dashboard Quick Guide</h4>
            <p>Data refreshes every 5 seconds. Use the sidebar to select different fridges and time ranges.</p>
        </div>
        """, unsafe_allow_html=True)

# Status tooltip
def create_status_tooltip():
    if st.session_state.show_tips:
        st.markdown(create_tooltip(
            "What does the status mean?", 
            "• <b>Operating normally</b>: Temperature between 2-6°C<br>"
            "• <b>Too cold</b>: Temperature below 2°C<br>"
            "• <b>Too warm</b>: Temperature above 6°C<br>"
            "• Door usage counts how many times the fridge was opened"
        ), unsafe_allow_html=True)