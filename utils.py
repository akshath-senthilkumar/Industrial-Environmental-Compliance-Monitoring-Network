import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import requests
import time

FIREBASE_URL = "https://compliancenet-9cc51-default-rtdb.asia-southeast1.firebasedatabase.app/live_data.json"

# --- SYNCHRONIZED THRESHOLDS (Must match your Pico W exactly) ---
THRESHOLDS = {
    "temp": 35.0,
    "aqi": 150.0,
    "noise": 80.0
}

def get_custom_css():
    return """
    <style>
        .main { background-color: #0E1117; color: #E0E6ED; }
        h1, h2, h3 { color: #E0E6ED; font-family: 'Inter', sans-serif; }
        .metric-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        /* NEW: Dimmed offline card styling */
        .metric-card.offline {
            opacity: 0.4;
            filter: grayscale(100%);
            border: 1px dashed #FF4B4B;
        }
        .metric-card:not(.offline):hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.08);
        }
        .metric-value { font-size: 2.2rem; font-weight: bold; color: #00FFAA; margin: 10px 0; }
        .metric-label { font-size: 1.1rem; color: #A0AEC0; text-transform: uppercase; letter-spacing: 1px; }
        
        .sdg-chip {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin-right: 15px;
            margin-bottom: 15px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .sdg-chip:hover {
            filter: brightness(1.2);
            cursor: pointer;
        }
        .sdg-3 { background-color: rgba(76, 159, 56, 0.15); border: 2px solid #4C9F38; color: #4C9F38; }
        .sdg-9 { background-color: rgba(253, 105, 37, 0.15); border: 2px solid #FD6925; color: #FD6925; }
        .sdg-11 { background-color: rgba(253, 157, 36, 0.15); border: 2px solid #FD9D24; color: #FD9D24; }
        .sdg-12 { background-color: rgba(191, 139, 46, 0.15); border: 2px solid #BF8B2E; color: #BF8B2E; }
    </style>
    """

def get_dashboard_data():
    """Fetches live data and adds a server-side arrival timestamp."""
    try:
        req_url = f'{FIREBASE_URL}?orderBy="$key"&limitToLast=100'
        response = requests.get(req_url)
        
        if response.status_code == 200 and response.json() is not None:
            raw_data = response.json()
            records = list(raw_data.values())
            df = pd.DataFrame(records)
            
            # Rename columns
            df = df.rename(columns={
                'temperature': 'Temperature (°C)',
                'gas_aqi': 'AQI (MQ-135)',
                'sound_db': 'Noise Level (dB)'
            })
            
            # Ensure status columns exist even if Firebase misses them on first boot
            for col in ['status_n1', 'status_n2', 'status_n3']:
                if col not in df.columns:
                    df[col] = "ON"
            
            # Record exactly when this data was fetched
            df['fetch_time'] = time.time() 
            
            # Create the Timestamp for your Plotly graphs
            if not df.empty:
                df['Timestamp'] = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='5s')
            
            return df
    except Exception as e:
        st.error(f"Error: {e}")
    return pd.DataFrame()

def metric_card(title, value, unit, threshold, current_val, icon="", is_offline=False):
    """Updated to support the offline 'dimmed' state."""
    if is_offline:
        card_class = "metric-card offline"
        display_val = "<span style='color:#FF4B4B; font-size: 1.5rem;'>OFFLINE</span>"
        subtext = "<span style='color:#FF4B4B;'>Check sensor power</span>"
    else:
        card_class = "metric-card"
        color = "#00FFAA" if current_val <= threshold else "#FF4B4B"
        display_val = f"<span style='color:{color}'>{value:.1f} <span style='font-size: 1.2rem; color: #A0AEC0;'>{unit}</span></span>"
        subtext = f"Threshold: {threshold} {unit}"

    st.markdown(f"""
        <div class="{card_class}">
            <div class="metric-label">{icon} {title}</div>
            <div class="metric-value">{display_val}</div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">{subtext}</div>
        </div>
    """, unsafe_allow_html=True)

def get_gateway_status(df):
    """Checks if the last data packet arrived within the last 15 seconds."""
    if df.empty or 'fetch_time' not in df.columns:
        return False
    
    # Get the time the latest row was actually fetched
    last_fetch = df['fetch_time'].iloc[-1]
    
    # If the current time is more than 15 seconds past the last fetch, it's offline
    return (time.time() - last_fetch) <= 15