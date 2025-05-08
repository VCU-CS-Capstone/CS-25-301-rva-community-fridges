# main.py
import streamlit as st
import config

def main():
    # 1) THIS must be your very first st.* call
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT
    )

    # 2) only now import anything that does st.* at import-time
    from components.login     import show_aws_login
    from components.dashboard import show_dashboard
    from components.map_view  import show_map_view
    from styles.custom_css    import apply_custom_css

    apply_custom_css()

    # 1) If we don't yet have AWS creds in session, show the login form
    if 'aws_access_key' not in st.session_state:
        show_aws_login()

    # 2) At this point we know we have credentials
    AWS_ACCESS_KEY = st.session_state.aws_access_key
    AWS_SECRET_KEY = st.session_state.aws_secret_key
    AWS_REGION     = st.session_state.aws_region

    # Now you can build your boto3 client for Timestream, e.g.:
    import boto3
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    # pass this session or client into your utilities
    from utils.aws import set_aws_session
    set_aws_session(session)
    
    # Initialize session state
    if 'show_tips' not in st.session_state:
        st.session_state.show_tips = True
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = False
    if 'show_map_welcome' not in st.session_state:
        st.session_state.show_map_welcome = False
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Dashboard", "Map View"], key="nav_radio")
    
    # Show tips toggle in sidebar
    #
    # Show tutorial button
    #

    # Display the selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Map View":
        show_map_view()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Streamlit AWS Timestream Fridge Monitoring Dashboard")
    
    # Add help section to sidebar
    with st.sidebar.expander("❓ Need Help?"):
        st.markdown(config.HELP_TEXT)
    
    # Add keyboard shortcuts helper
    #with st.sidebar.expander("⌨️ Keyboard Shortcuts"):
    #    st.markdown(config.KEYBOARD_SHORTCUTS)
    
    # Add timestamp for last refresh
    from datetime import datetime
    st.sidebar.caption(f"Last refreshed: {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}")

if __name__ == "__main__":
    main()