import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    /* Tooltip styles */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 250px;
        background-color: #555;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -125px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 14px;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 0.95;
    }
    
    /* Guide card styles */
    .guide-card {
        background: linear-gradient(90deg, #1E88E5 0%, #64B5F6 100%);
        color: white;
        margin: 10px 0;
        padding: 16px;
        border-radius: 6px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Welcome banner styles */
    .welcome-banner {
        background: linear-gradient(90deg, #1E88E5 0%, #64B5F6 100%);
        color: white;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .close-button {
        float: right;
        background: rgba(255,255,255,0.3);
        border: none;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
        cursor: pointer;
    }
    
    /* Modal popup styles */
    .modal-overlay {
        display: flex;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        justify-content: center;
        align-items: center;
    }
    
    .modal-content {
        background: linear-gradient(90deg, #1E88E5 0%, #64B5F6 100%);
        color: white;
        width: 80%;
        max-width: 800px;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        position: relative;
        animation: modalFadeIn 0.5s ease;
    }
    
    @keyframes modalFadeIn {
        from {opacity: 0; transform: translateY(-50px);}
        to {opacity: 1; transform: translateY(0);}
    }
    
    .modal-close {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(255,255,255,0.3);
        border: none;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        font-size: 18px;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        transition: background 0.3s;
    }
    
    .modal-close:hover {
        background: rgba(255,255,255,0.5);
    }
    
    .modal-button {
        background-color: white;
        color: #1E88E5;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
        margin-top: 15px;
        transition: background 0.3s;
    }
    
    .modal-button:hover {
        background-color: #f0f0f0;
    }
    
    /* Status indicator styles */
    .status-indicator {
        padding: 10px;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin-top: 25px;
        font-weight: bold;
    }
    
    /* Feature highlight styles */
    .feature-highlight {
        border: 1px dashed;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to get status indicator style
def get_status_indicator_style(status, color):
    return f"""
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
    """

def color_status_style():
    def color_status(val):
        if "Normal" in val:
            return 'background-color: #c6efce; color: #006100'
        elif "cold" in val:
            return 'background-color: #bdd7ee; color: #1f497d'
        elif "warm" in val:
            return 'background-color: #ffc7ce; color: #9c0006'
        else:  # No data
            return 'background-color: #f2f2f2; color: #666666'
    return color_status

# Color map for plotly charts
def get_status_color_map():
    return {
        "Normal": "#c6efce", 
        "Too cold": "#bdd7ee", 
        "Too warm": "#ffc7ce",
        "No data": "#f2f2f2"
    }