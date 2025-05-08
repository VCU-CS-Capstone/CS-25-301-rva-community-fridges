# components/login.py
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# Create one cookie manager for this component
cookies = EncryptedCookieManager(
    prefix="aws",                   # cookie names will be aws_access_key, aws_secret_key, aws_region
    password="diajdiajwdijawdiwjidjawidjiwajdiajwidjiwajd",  
)
if not cookies.ready():
    # Wait until the cookie lib has initialized
    st.stop()

def show_aws_login():
    # Pre-fill from cookies (if they exist)
    default_key    = cookies.get("access_key", "")
    default_secret = cookies.get("secret_key", "")
    default_region = cookies.get("region", "us-east-1")

    with st.form("aws_login", clear_on_submit=False):
        access_key = st.text_input("AWS Access Key ID", value=default_key)
        secret_key = st.text_input("AWS Secret Access Key", value=default_secret, type="password")
        region     = st.text_input("AWS Region", value=default_region)
        remember   = st.checkbox("Remember me", value=bool(default_key and default_secret))
        submitted  = st.form_submit_button("Log in")

    if submitted:
        if not access_key or not secret_key:
            st.error("Both key and secret are required.")
        else:
            # Store into session_state for immediate use
            st.session_state.aws_access_key = access_key
            st.session_state.aws_secret_key = secret_key
            st.session_state.aws_region     = region

            # Persist into encrypted cookies if “remember me” is checked
            if remember:
                cookies["access_key"] = access_key
                cookies["secret_key"] = secret_key
                cookies["region"]     = region
            else:
                # clear out any old values
                cookies["access_key"] = ""
                cookies["secret_key"] = ""
                cookies["region"]     = ""
            cookies.save()  # write back to the browser

            # and now we can rerun
            st.rerun()

    # If you reach here, nobody’s logged in yet
    st.stop()
