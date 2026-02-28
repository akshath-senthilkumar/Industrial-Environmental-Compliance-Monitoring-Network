import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

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
        .metric-card:hover {
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

@st.cache_data
def generate_data():
    now = datetime.now()
    dates = [now - timedelta(minutes=i*2) for i in range(150)]
    dates.reverse()
    
    df = pd.DataFrame({
        'Timestamp': dates,
        'Temperature (°C)': [np.random.normal(26, 1.5) + np.sin(i*0.1)*2 for i in range(150)],
        'AQI (MQ-135)': [np.clip(np.random.normal(110, 20) + (i*0.2), 50, 300) for i in range(150)],
        'Noise Level (dB)': [np.random.normal(68, 5) + np.random.choice([0, 15, 25], p=[0.9, 0.08, 0.02]) for i in range(150)],
    })
    return df

def metric_card(title, value, unit, threshold, current_val, icon=""):
    color = "#00FFAA" if current_val <= threshold else "#FF4B4B"
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {title}</div>
            <div class="metric-value" style="color: {color}">{value:.1f} <span style="font-size: 1.2rem; color: #A0AEC0;">{unit}</span></div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Threshold: {threshold} {unit}</div>
        </div>
    """, unsafe_allow_html=True)
