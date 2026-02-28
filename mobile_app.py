import streamlit as st
from streamlit_autorefresh import st_autorefresh  # <-- 1. Added Auto-refresh
from utils import get_dashboard_data, get_custom_css, get_gateway_status, THRESHOLDS

# Ensure mobile-friendly initial viewport scaling 
st.set_page_config(page_title="Mobile Field App", page_icon="📱", layout="centered")

# 3. Auto-refresh the mobile view every 5 seconds
st_autorefresh(interval=5000, limit=None, key="mobile_dashboard_refresh")

# Inject a meta viewport tag and remove padding for true mobile feel
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
    <style>
        /* Override Streamlit's default padding to look native on mobile */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .main { background-color: #0E1117; color: #E0E6ED; }
        h1, h2, h3 { color: #E0E6ED; font-family: 'Inter', sans-serif; }
        
        /* Mobile Specific Overrides */
        .mobile-header {
            text-align: center;
            padding: 20px 0 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            background: linear-gradient(180deg, rgba(0,255,170,0.1) 0%, rgba(14,17,23,0) 100%);
        }
        .mobile-metric {
            margin: 10px 0;
            padding: 20px;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
        }
        .mobile-metric.offline {
            opacity: 0.4;
            filter: grayscale(100%);
            border: 1px dashed #FF4B4B;
        }
        .status-badge {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
        }
    </style>
""", unsafe_allow_html=True)

# 4. Fetch live data and add the safety check
df = get_dashboard_data()

if not df.empty:
    current_data = df.iloc[-1]
    gateway_online = get_gateway_status(df)
else:
    # Safe fallback zeros while waiting for the Fog Node to connect
    current_data = {'Temperature (°C)': 0, 'AQI (MQ-135)': 0, 'Noise Level (dB)': 0, 'status_n1': 'OFF', 'status_n2': 'OFF', 'status_n3': 'OFF'}
    gateway_online = False

# Mobile UI logic for the Gateway Watchdog
if gateway_online:
    fog_status_text = "🟢 GATEWAY ONLINE"
    fog_status_color = "#00FFAA"
else:
    fog_status_text = "🔴 GATEWAY OFFLINE"
    fog_status_color = "#FF4B4B"

# Extract Node Statuses
n1_offline = current_data.get('status_n1') == 'OFF'
n2_offline = current_data.get('status_n2') == 'OFF'
n3_offline = current_data.get('status_n3') == 'OFF'

# Dynamic HTML Generation for Node 1 (Temp)
if n1_offline:
    t_html = '<span style="color:#FF4B4B; font-size:1.5rem; font-weight:bold;">OFFLINE</span>'
else:
    t_html = f'<span style="font-size:1.8rem; font-weight:bold; color: #E0E6ED;">{current_data["Temperature (°C)"]:.1f}°C</span>'

# Dynamic HTML Generation for Node 2 (AQI)
aqi_val = current_data['AQI (MQ-135)']
border_color = '#FF4B4B' if (not n2_offline and aqi_val > THRESHOLDS['aqi']) else '#00FFAA'
warning_html = '<div style="font-size: 0.8rem; color: #FF4B4B; margin-top: 5px;">⚠ Elevated levels detected</div>' if (not n2_offline and aqi_val > THRESHOLDS['aqi']) else ''

if n2_offline:
    a_html = '<span style="color:#FF4B4B; font-size:1.5rem; font-weight:bold;">OFFLINE</span>'
    border_color = '#FF4B4B'
else:
    a_html = f'<span style="font-size:1.8rem; font-weight:bold; color: #E0E6ED;">{aqi_val:.0f} AQI</span>'

# Dynamic HTML Generation for Node 3 (Noise)
if n3_offline:
    n_html = '<span style="color:#FF4B4B; font-size:1.5rem; font-weight:bold;">OFFLINE</span>'
else:
    n_html = f'<span style="font-size:1.8rem; font-weight:bold; color: #E0E6ED;">{current_data["Noise Level (dB)"]:.1f} dB</span>'

st.markdown(f"""
<div class="mobile-header">
    <h2 style="margin:0; font-size: 1.5rem;">EcoMonitor Field App</h2>
    <span style="color:#00FFAA; font-size: 0.8rem;">● Zigbee Network Sync</span>
</div>
<div style="padding: 10px 0;">
    <div class="mobile-metric {'offline' if n1_offline else ''}">
        <span style="color:#A0AEC0; font-size: 0.9rem; text-transform: uppercase;">🌡️ Ambient State (DHT11)</span><br>
        {t_html}
    </div>
    <div class="mobile-metric {'offline' if n2_offline else ''}" style="border-left: 4px solid {border_color};">
        <span style="color:#A0AEC0; font-size: 0.9rem; text-transform: uppercase;">💨 Gases (MQ-135)</span><br>
        {a_html}
        {warning_html}
    </div>
    <div class="mobile-metric {'offline' if n3_offline else ''}">
        <span style="color:#A0AEC0; font-size: 0.9rem; text-transform: uppercase;">🔊 Acoustic (KY-038)</span><br>
        {n_html}
    </div>
    
    <div class="status-badge">
        <span style="color: {fog_status_color}; font-weight: 800; font-size: 1.1rem; letter-spacing: 1px;">{fog_status_text}</span><br>
    </div>
</div>
""", unsafe_allow_html=True)