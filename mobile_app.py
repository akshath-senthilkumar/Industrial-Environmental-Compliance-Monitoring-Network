import streamlit as st
from utils import generate_data, get_custom_css

# Ensure mobile-friendly initial viewport scaling 
st.set_page_config(page_title="Mobile Field App", page_icon="📱", layout="centered")

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
        .sync-btn {
            background: linear-gradient(90deg, #00FFAA, #00B8FF);
            color: #0E1117;
            border: none;
            padding: 15px 20px;
            border-radius: 25px;
            width: 100%;
            font-weight: 800;
            font-size: 1.1rem;
            cursor: pointer;
            display: block;
            margin: 20px auto;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,255,170,0.3);
        }
    </style>
""", unsafe_allow_html=True)

df = generate_data()
current_data = df.iloc[-1]

st.markdown(f"""
<div class="mobile-header">
    <h2 style="margin:0; font-size: 1.5rem;">EcoMonitor Field App</h2>
    <span style="color:#00FFAA; font-size: 0.8rem;">● Zigbee Network Sync</span>
</div>
<div style="padding: 10px 0;">
    <div class="mobile-metric">
        <span style="color:#A0AEC0; font-size: 0.9rem; text-transform: uppercase;">🌡️ Ambient State (DHT11)</span><br>
        <span style="font-size:1.8rem; font-weight:bold; color: #E0E6ED;">{current_data['Temperature (°C)']:.1f}°C</span>
    </div>
    <div class="mobile-metric" style="border-left: 4px solid {'#FF4B4B' if current_data['AQI (MQ-135)'] > 120 else '#00FFAA'};">
        <span style="color:#A0AEC0; font-size: 0.9rem; text-transform: uppercase;">💨 Gases (MQ-135)</span><br>
        <span style="font-size:1.8rem; font-weight:bold; color: #E0E6ED;">{current_data['AQI (MQ-135)']:.0f} AQI</span>
        <div style="font-size: 0.8rem; color: #FF4B4B; margin-top: 5px;">⚠ Elevated levels detected</div>
    </div>
    <div class="mobile-metric">
        <span style="color:#A0AEC0; font-size: 0.9rem; text-transform: uppercase;">🔊 Acoustic (KY-038)</span><br>
        <span style="font-size:1.8rem; font-weight:bold; color: #E0E6ED;">{current_data['Noise Level (dB)']:.1f} dB</span>
    </div>
    <div class="sync-btn">
        SYNC DATA to GATEWAY
    </div>
</div>
""", unsafe_allow_html=True)
