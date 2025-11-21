# app.py - Fyers API v3 Working Template
"""
Fyers API v3 Integration - Updated for 2025
Simple REST approach with correct v3 endpoints
"""

import streamlit as st
import requests
import json
import pandas as pd
import hashlib

st.set_page_config(page_title="Fyers API v3 - Live NSE Data", layout="wide")

st.title("🚀 Fyers API v3 - Real Indian Market Data")

# Sidebar for credentials
st.sidebar.header("Fyers API v3 Credentials")
st.sidebar.markdown("Get these from: https://myapi.fyers.in/dashboard/")

app_id = st.sidebar.text_input("App ID", help="Your Fyers App ID (format: XXXXX-100)")
secret_key = st.sidebar.text_input("Secret Key", type="password", help="Your App Secret")
redirect_uri = st.sidebar.text_input("Redirect URI", value="https://127.0.0.1/")

# Main content
st.markdown("""
### 📋 Fyers API v3 Setup Guide

**Step 1:** Enter your App ID and Secret Key in the sidebar  
**Step 2:** Click "Generate Login URL" below  
**Step 3:** Open the URL in browser and authorize  
**Step 4:** Copy the `auth_code` from redirected URL  
**Step 5:** Paste auth_code and click Authenticate
""")

# Generate app_id_hash (required for v3)
app_id_hash = ""
if app_id and secret_key:
    # Create hash: app_id + ":" + secret_key
    hash_string = f"{app_id}:{secret_key}"
    app_id_hash = hashlib.sha256(hash_string.encode()).hexdigest()
    
    st.info(f"✅ App ID Hash generated: {app_id_hash[:20]}...")

# Generate login URL
if app_id and redirect_uri:
    # v3 uses different URL structure
    login_url = f"https://api-t1.fyers.in/api/v3/generate-authcode?client_id={app_id}&redirect_uri={redirect_uri}&response_type=code&state=sample_state"
    
    if st.button("📋 Generate Login URL", key="gen_url"):
        st.markdown("### 🔗 Step 2: Copy this URL and open in browser")
        st.code(login_url, language='text')
        st.info("⬆️ After login, you'll be redirected. Copy the `auth_code` from the URL")
        st.markdown("**URL will look like:** `https://127.0.0.1/?auth_code=XXXXXX&s
