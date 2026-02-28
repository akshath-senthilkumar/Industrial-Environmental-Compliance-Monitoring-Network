import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh  # Add this!

# Swap generate_data for get_dashboard_data
from utils import get_dashboard_data, get_custom_css, metric_card 

st.set_page_config(
    page_title="Industrial Regulatory Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh the entire page every 5 seconds (5000 ms)
st_autorefresh(interval=5000, limit=None, key="live_dashboard_refresh")

st.markdown(get_custom_css(), unsafe_allow_html=True)

# Fetch the live Firebase data
df = get_dashboard_data()

# Protect against app crashes if the database is completely empty on first boot
if not df.empty:
    current_data = df.iloc[-1]
else:
    # Safe fallback zeros while waiting for the Fog Node to connect
    current_data = {'Temperature (°C)': 0, 'AQI (MQ-135)': 0, 'Noise Level (dB)': 0}

# ---------------------------------------------------------
# EVERYTHING BELOW THIS LINE STAYS EXACTLY THE SAME!
# with st.sidebar:
# ...

with st.sidebar:
    st.markdown("## 🌍 ComplianceNet Pro")
    st.caption("AI-Driven Regulatory Monitoring")
    st.markdown("---")
    st.markdown("### 📡 Network Status")
    st.success("✅ **Zigbee Mesh**: 3 Sensor Nodes Active")
    st.info("🔄 **Collector Node**: Syncing (12ms ping)")
    st.warning("🤖 **Microcontroller Process**: Analyzing Logs")
    st.caption(f"Last Gateway Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")
    view_mode = st.radio("Select View Context:", [
        "📊 Main Dashboard", 
        "⚙️ Hardware Architecture", 
        "🎯 SDG Alignment"
    ])
    st.markdown("---")
    st.download_button(
        label="📄 Generate Audit Report",
        data="MOCK REPORT DATA FOR AUDITOR...",
        file_name="compliance_report_Q1.pdf",
        mime="application/pdf"
    )

if view_mode == "📊 Main Dashboard":
    st.title("🏭 Continuous Compliance Dashboard")
    st.markdown("Automated generation of continuous logs and AI-based trend detection for factory auditors.")

    # KPIs Top Row - Removed Humidity and PM Emissions
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Temperature", current_data['Temperature (°C)'], "°C", 35, current_data['Temperature (°C)'], "🌡️")
    with col2:
        metric_card("Air Quality", current_data['AQI (MQ-135)'], "AQI", 150, current_data['AQI (MQ-135)'], "💨")
    with col3:
        metric_card("Noise Level", current_data['Noise Level (dB)'], "dB", 80, current_data['Noise Level (dB)'], "🔊")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Graphs
    colA, colB = st.columns(2)
    with colA:
        st.subheader("🤖 AI Trend Detection: Air Quality")
        fig_aqi = px.area(df, x='Timestamp', y=['AQI (MQ-135)'],
                          color_discrete_sequence=['#FF4B4B'])
        fig_aqi.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(255,255,255,0.02)', 
            font_color='#E0E6ED',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_aqi, width='stretch')
        
    with colB:
        st.subheader("🌡️ Ambient Working Conditions (Temp)")
        fig_th = px.line(df, x='Timestamp', y=['Temperature (°C)'], 
                         color_discrete_sequence=['#00FFAA'])
        fig_th.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(255,255,255,0.02)', 
            font_color='#E0E6ED',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_th, width='stretch')

elif view_mode == "⚙️ Hardware Architecture":
    st.title("⚙️ System Architecture & Hardware Specs")
    st.markdown("Distributed compliance monitoring network ensuring factories meet air quality, noise, and temperature norms.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### 🧠 Edge Sensor Nodes & Network
        * **3x Sensor Nodes (STM32)**: Remote nodes handling data acquisition, sensor timing, and alert prioritization.
        * **1x Collector Node**: Gathers data from the 3 sensor nodes via Zigbee and sends it to the central microcontroller for processing.
        * **Wireless Mesh (Zigbee)**: Self-healing, industrially robust mesh network connecting the nodes across the factory floor.
        * **Central Microcontroller Process**: Aggregates sensor data, timestamps, validates, and pushes to the Web / AI APIs.
        """)
        
        st.markdown("### 📡 Sensor Matrix")
        st.table(pd.DataFrame({
            "Measurement": ["Gas Sensors (Air Quality)", "Sound Level Sensors (Noise)", "Temperature Sensors"],
            "Regulatory Focus": ["Hazardous Gas Exposure", "Occupational Noise Safety", "Ambient Working Conditions"]
        }))
        
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
            <h4 style="margin-top:0;">Data Flow</h4>
            <pre style="background: transparent; border: none; font-size: 0.9rem; color: #00FFAA;">
3x SENSOR NODES (STM32)
   │ (Gas, Sound, Temp)
   ▼
ZIGBEE WIRELESS MESH
   │
   ▼
1x COLLECTOR NODE
   │ (Aggregates)
   ▼
MAIN MICROCONTROLLER
   │ (Validates, Processes)
   ▼
WEB + AI APIs
   │ (Trend Detection)
   ▼
<b>Regulatory Dashboard</b>
            </pre>
        </div>
        """, unsafe_allow_html=True)

elif view_mode == "🎯 SDG Alignment":
    st.title("🎯 SDG Alignment & Regulatory Compliance")
    st.markdown("This system is mandatory in many regions to avoid shutdowns and fines. Manual inspection is unreliable, and auditors require continuous logs.")

    st.markdown("""
    <div style="margin: 20px 0;">
        <div class="sdg-chip sdg-3">SDG 3: Good Health & Well-Being</div>
        <div class="sdg-chip sdg-9">SDG 9: Industry & Infrastructure</div>
        <div class="sdg-chip sdg-11">SDG 11: Sustainable Cities</div>
        <div class="sdg-chip sdg-12">SDG 12: Responsible Production</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🌿 SDG 3: Good Health and Well-being
        **Target 3.9**: By 2030, substantially reduce the number of deaths and illnesses from hazardous chemicals and air, water and soil pollution.
        > *Implemented via continuous tracking of occupational hazards (gases, noise) to ensure worker safety.*
        
        ### 🏙️ SDG 11: Sustainable Cities
        **Target 11.6**: Reduce the adverse per capita environmental impact of cities, including by paying special attention to air quality.
        > *Dashboard provides verifiable air quality logs for auditors to prevent community pollution.*
        """)
        
    with col2:
        st.markdown("""
        ### 🏗️ SDG 9: Industry & Infrastructure
        **Target 9.4**: Upgrade infrastructure and retrofit industries to make them sustainable, with increased resource-use efficiency.
        > *Upgrading legacy factories with **Zigbee Mesh** and **AI Trend Detection** establishes modernized, verifiable infrastructure.*
        
        ### ♻️ SDG 12: Responsible Production
        **Target 12.4**: Achieve environmentally sound management of chemicals and wastes... reducing their release to air.
        > *Real-time continuous logging ensures industrial production remains strictly within regulatory norms.*
        """)
