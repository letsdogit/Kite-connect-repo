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
        st.markdown("**URL will look like:** `https://127.0.0.1/?auth_code=XXXXXX&state=sample_state`")

# Auth code input
st.markdown("---")
auth_code = st.text_input("Step 4: Paste your auth_code here:", type="password", 
                          help="Copy only the code part after auth_code= in the redirected URL")

# Authenticate button
if st.button("🔐 Authenticate with Fyers v3", type="primary"):
    if not all([app_id, secret_key, auth_code, app_id_hash]):
        st.error("⚠️ Please fill all fields: App ID, Secret Key, and auth_code")
    else:
        with st.spinner("Authenticating with Fyers v3..."):
            try:
                # v3 token endpoint
                token_url = "https://api-t1.fyers.in/api/v3/validate-authcode"
                
                payload = {
                    "grant_type": "authorization_code",
                    "appIdHash": app_id_hash,
                    "code": auth_code
                }
                
                headers = {"Content-Type": "application/json"}
                
                st.write("Debug - Sending request to:", token_url)
                st.write("Debug - Payload:", {**payload, "appIdHash": f"{app_id_hash[:20]}..."})
                
                response = requests.post(token_url, json=payload, headers=headers)
                
                st.write(f"Debug - Response status: {response.status_code}")
                st.write(f"Debug - Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("s") == "ok" and "access_token" in data:
                        access_token = data["access_token"]
                        
                        # Store in session
                        st.session_state.access_token = access_token
                        st.session_state.app_id = app_id
                        st.session_state.authenticated = True
                        
                        st.success("✅ Authentication successful!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Authentication failed: {data}")
                else:
                    st.error(f"❌ HTTP Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# Show data fetching interface if authenticated
if st.session_state.get('authenticated'):
    st.markdown("---")
    st.success("🟢 Connected to Fyers API v3")
    
    access_token = st.session_state.access_token
    app_id = st.session_state.app_id
    
    # v3 uses different auth header format
    auth_header = {
        "Authorization": f"{app_id}:{access_token}"
    }
    
    # Tabs for different data
    tab1, tab2, tab3 = st.tabs(["📊 Live Quotes", "👤 Profile", "📈 Historical Data"])
    
    with tab1:
        st.subheader("Get Live Market Quotes (v3)")
        
        symbol = st.text_input("Enter Symbol", value="NSE:NIFTYBANK-INDEX", 
                               help="Format: NSE:SYMBOL or NSE:SYMBOL-INDEX")
        
        if st.button("Get Quote", key="quote_btn"):
            try:
                # v3 quotes endpoint
                quote_url = "https://api-t1.fyers.in/data-rest/v3/quotes/"
                params = {"symbols": symbol}
                
                response = requests.get(quote_url, params=params, headers=auth_header)
                
                st.write(f"Debug - Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    st.json(data)
                    
                    # Pretty display
                    if "d" in data and len(data["d"]) > 0:
                        quote = data["d"][0]["v"]
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Last Price", f"₹{quote.get('lp', 0):,.2f}")
                        col2.metric("Volume", f"{quote.get('volume', 0):,.0f}")
                        col3.metric("Change %", f"{quote.get('ch_per', 0):.2f}%")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Your Profile (v3)")
        
        if st.button("Get Profile", key="profile_btn"):
            try:
                # v3 profile endpoint
                profile_url = "https://api-t1.fyers.in/api/v3/profile"
                
                response = requests.get(profile_url, headers=auth_header)
                
                st.write(f"Debug - Status: {response.status_code}")
                
                if response.status_code == 200:
                    profile = response.json()
                    st.json(profile)
                    
                    if "data" in profile:
                        st.success(f"✅ Name: {profile['data'].get('name', 'N/A')}")
                        st.info(f"📧 Email: {profile['data'].get('email_id', 'N/A')}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("Historical Data (v3)")
        st.info("💡 Note: Historical data requires subscription")
        
        col1, col2 = st.columns(2)
        with col1:
            hist_symbol = st.text_input("Symbol", value="NSE:SBIN-EQ", key="hist_symbol")
            resolution = st.selectbox("Resolution", ["1", "5", "15", "60", "D"], index=2)
        
        with col2:
            from_date = st.date_input("From Date")
            to_date = st.date_input("To Date")
        
        if st.button("Get Historical Data", key="hist_btn"):
            try:
                # v3 history endpoint
                hist_url = "https://api-t1.fyers.in/data-rest/v3/history/"
                
                # Convert dates to unix timestamp
                from_ts = int(pd.Timestamp(from_date).timestamp())
                to_ts = int(pd.Timestamp(to_date).timestamp())
                
                params = {
                    "symbol": hist_symbol,
                    "resolution": resolution,
                    "date_format": "0",  # Unix timestamp
                    "range_from": from_ts,
                    "range_to": to_ts,
                    "cont_flag": "1"
                }
                
                response = requests.get(hist_url, params=params, headers=auth_header)
                
                st.write(f"Debug - Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "candles" in data:
                        # Create DataFrame
                        df = pd.DataFrame(data["candles"], 
                                        columns=["timestamp", "open", "high", "low", "close", "volume"])
                        df["datetime"] = pd.to_datetime(df["timestamp"], unit='s')
                        
                        st.dataframe(df[["datetime", "open", "high", "low", "close", "volume"]], 
                                   use_container_width=True, height=300)
                        
                        st.line_chart(df.set_index("datetime")["close"])
                    else:
                        st.warning(f"No data available. Response: {data}")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())

# Logout button
if st.session_state.get('authenticated'):
    st.markdown("---")
    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#666;font-size:12px;'>
<p><strong>Fyers API v3 - Updated Integration (2025)</strong></p>
<p>✅ Using latest v3 endpoints • No complex dependencies • Easy to deploy</p>
<p>⚠️ Keep your credentials secure • Never share access tokens publicly</p>
</div>
""", unsafe_allow_html=True)
