import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from utils import get_dashboard_data, get_custom_css, metric_card, get_gateway_status, THRESHOLDS, generate_audit_report_pdf

st.set_page_config(
    page_title="Industrial Regulatory Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, limit=None, key="live_dashboard_refresh")

st.markdown(get_custom_css(), unsafe_allow_html=True)

# Fetch live Firebase data
df = get_dashboard_data()

if not df.empty:
    current_data = df.iloc[-1]
    gateway_online = get_gateway_status(current_data)
else:
    current_data = {'Temperature (°C)': 0, 'AQI (MQ-135)': 0, 'Noise Level (dB)': 0, 'status_n1': 'OFF', 'status_n2': 'OFF', 'status_n3': 'OFF'}
    gateway_online = False

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 10px 0 5px 0;">
        <span style="font-size:2rem;">🏭</span>
        <h2 style="margin:4px 0 2px 0; font-size:1.2rem; color:#E0E6ED;">ComplianceNet Pro</h2>
        <span style="font-size:0.78rem; color:#00FFAA; letter-spacing:1px;">INDUSTRIAL MONITORING</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📡 Network Status")

    if gateway_online:
        st.success("✅ **Gateway Node**: ONLINE")
        st.info("🔄 **Collector Node**: Syncing")
    else:
        st.error("❌ **Gateway Node**: OFFLINE")
        st.warning("⚠️ **Collector Node**: Connection Lost")

    st.caption(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")

    view_mode = st.radio("Select View:", [
        "📊 Main Dashboard",
        "⚙️ Hardware Architecture",
        "🎯 SDG Alignment"
    ])

    st.markdown("---")
    report_filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    st.download_button(
        label="📄 Generate Audit Report",
        data=generate_audit_report_pdf(df, current_data, gateway_online),
        file_name=report_filename,
        mime="application/pdf",
        use_container_width=True
    )

# ── Main Dashboard ─────────────────────────────────────────────────────────────
if view_mode == "📊 Main Dashboard":
    st.markdown("""
    <div style="margin-bottom: 8px;">
        <h1 style="margin:0; font-size:1.9rem; color:#E0E6ED;">
            🏭 Continuous Compliance Dashboard
        </h1>
        <p style="color:#A0AEC0; margin-top:4px; font-size:0.95rem;">
            Real-time environmental monitoring from factory floor sensor nodes
        </p>
    </div>
    """, unsafe_allow_html=True)

    n1_offline = current_data.get('status_n1') == 'OFF'
    n2_offline = current_data.get('status_n2') == 'OFF'
    n3_offline = current_data.get('status_n3') == 'OFF'

    # KPI Row
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Temperature", current_data['Temperature (°C)'], "°C", THRESHOLDS['temp'], current_data['Temperature (°C)'], "🌡️", n1_offline)
    with col2:
        metric_card("AQI", current_data['AQI (MQ-135)'], "AQI", THRESHOLDS['aqi'], current_data['AQI (MQ-135)'], "💨", n2_offline)
    with col3:
        metric_card("Sound", current_data['Noise Level (dB)'], "dB", THRESHOLDS['noise'], current_data['Noise Level (dB)'], "🔊", n3_offline)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts: Row 1 — AQI + Temperature ─────────────────────────────────────
    colA, colB = st.columns(2)

    chart_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.02)',
        font_color='#E0E6ED',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=260
    )

    with colA:
        st.markdown("""
        <p style="font-size:1rem; font-weight:600; color:#E0E6ED; margin:0 0 6px 0; letter-spacing:0.5px;">
            💨 AQI
        </p>""", unsafe_allow_html=True)
        if not df.empty:
            fig_aqi = px.area(df, x='Timestamp', y='AQI (MQ-135)', color_discrete_sequence=['#FF4B4B'])
            fig_aqi.update_traces(fill='tozeroy', fillcolor='rgba(255,75,75,0.12)', line=dict(width=2))
            fig_aqi.update_layout(**chart_layout)
            fig_aqi.add_hline(y=THRESHOLDS['aqi'], line_dash="dot", line_color="rgba(255,75,75,0.5)",
                              annotation_text=f"Limit: {THRESHOLDS['aqi']}", annotation_font_color="#FF4B4B")
            st.plotly_chart(fig_aqi, use_container_width=True)

    with colB:
        st.markdown("""
        <p style="font-size:1rem; font-weight:600; color:#E0E6ED; margin:0 0 6px 0; letter-spacing:0.5px;">
            🌡️ Temperature
        </p>""", unsafe_allow_html=True)
        if not df.empty:
            fig_temp = px.line(df, x='Timestamp', y='Temperature (°C)', color_discrete_sequence=['#00FFAA'])
            fig_temp.update_traces(line=dict(width=2.5))
            fig_temp.update_layout(**chart_layout)
            fig_temp.add_hline(y=THRESHOLDS['temp'], line_dash="dot", line_color="rgba(0,255,170,0.4)",
                               annotation_text=f"Limit: {THRESHOLDS['temp']}°C", annotation_font_color="#00FFAA")
            st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Charts: Row 2 — Sound (full width) ────────────────────────────────────
    st.markdown("""
    <p style="font-size:1rem; font-weight:600; color:#E0E6ED; margin:0 0 6px 0; letter-spacing:0.5px;">
        🔊 Sound in dB
    </p>""", unsafe_allow_html=True)
    if not df.empty:
        fig_noise = go.Figure()
        fig_noise.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=df['Noise Level (dB)'],
            mode='lines',
            name='Sound (dB)',
            line=dict(color='#A78BFA', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(167,139,250,0.10)'
        ))
        noise_layout = dict(**chart_layout)
        noise_layout['height'] = 240
        fig_noise.update_layout(**noise_layout)
        fig_noise.add_hline(y=THRESHOLDS['noise'], line_dash="dot", line_color="rgba(167,139,250,0.5)",
                            annotation_text=f"Limit: {THRESHOLDS['noise']} dB", annotation_font_color="#A78BFA")
        st.plotly_chart(fig_noise, use_container_width=True)

# ── Hardware Architecture ──────────────────────────────────────────────────────
elif view_mode == "⚙️ Hardware Architecture":
    st.title("⚙️ System Architecture & Hardware Specs")
    st.markdown("Distributed compliance monitoring network ensuring factories meet air quality, noise, and temperature norms.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### 🧠 Edge Sensor Nodes & Network
        * **3x Sensor Nodes (STM32)**: Remote nodes handling data acquisition, sensor timing, and alert prioritization.
        * **1x Collector Node**: Gathers data from the 3 sensor nodes via Zigbee and sends it to the central gateway for processing.
        * **Wireless Mesh (Zigbee)**: Self-healing, industrially robust mesh network connecting the nodes across the factory floor.
        * **Gateway Node**: Aggregates sensor data, timestamps, validates, and pushes to the Firebase database.
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
GATEWAY NODE
   │ (Validates, Pushes)
   ▼
FIREBASE DATABASE
   │
   ▼
<b>Regulatory Dashboard</b>
            </pre>
        </div>
        """, unsafe_allow_html=True)

# ── SDG Alignment ──────────────────────────────────────────────────────────────
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
        > *Upgrading legacy factories with **Zigbee Mesh** establishes modernized, verifiable infrastructure.*

        ### ♻️ SDG 12: Responsible Production
        **Target 12.4**: Achieve environmentally sound management of chemicals and wastes... reducing their release to air.
        > *Real-time continuous logging ensures industrial production remains strictly within regulatory norms.*
        """)