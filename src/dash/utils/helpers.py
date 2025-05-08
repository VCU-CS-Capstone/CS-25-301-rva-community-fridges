from datetime import datetime
import streamlit as st

def unique_key(prefix=""):
    """Generate a unique key for Streamlit elements to avoid duplicate IDs"""
    return f"{prefix}_{datetime.now().timestamp()}_{id(datetime.now())}"

def safe_plotly_chart(fig, use_container_width=True, prefix="plot"):
    """Display a plotly chart with a guaranteed unique key"""
    key = unique_key(prefix)
    return st.plotly_chart(fig, use_container_width=use_container_width, key=key)

def create_tooltip(text, tip_text):
    """Create an HTML tooltip"""
    return f"""
    <div class="tooltip">{text} ⓘ
        <span class="tooltiptext">{tip_text}</span>
    </div>
    """