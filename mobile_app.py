import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils import get_dashboard_data, get_custom_css, get_gateway_status, THRESHOLDS
import plotly.graph_objects as go

st.set_page_config(page_title="ComplianceNet Pro", page_icon="📱", layout="centered")

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, limit=None, key="mobile_dashboard_refresh")

# Inject global styles
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .main { background-color: #0E1117; color: #E0E6ED; }
        h1, h2, h3 { color: #E0E6ED; }

        /* App header */
        .app-header {
            text-align: center;
            padding: 18px 0 14px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            background: linear-gradient(180deg, rgba(0,255,170,0.08) 0%, rgba(14,17,23,0) 100%);
            margin-bottom: 14px;
        }
        .app-header h2 {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 800;
            color: #E0E6ED;
            letter-spacing: 0.5px;
        }
        .app-header .subtitle {
            color: #00FFAA;
            font-size: 0.75rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 3px;
        }

        /* Metric cards */
        .m-card {
            margin: 10px 0;
            padding: 18px 20px;
            border-radius: 16px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.09);
            backdrop-filter: blur(14px);
            transition: transform 0.2s ease;
        }
        .m-card.offline {
            opacity: 0.4;
            filter: grayscale(100%);
            border: 1px dashed #FF4B4B;
        }
        .m-card-label {
            font-size: 0.78rem;
            color: #7C8FAC;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .m-card-value {
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.15;
        }
        .m-card-sub {
            font-size: 0.75rem;
            color: #596577;
            margin-top: 5px;
        }
        .m-warning {
            font-size: 0.78rem;
            color: #FF4B4B;
            margin-top: 5px;
            font-weight: 600;
        }

        /* Status badge */
        .status-badge {
            margin-top: 16px;
            padding: 14px;
            border-radius: 14px;
            text-align: center;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
        }
        .status-text {
            font-weight: 800;
            font-size: 1rem;
            letter-spacing: 1.5px;
        }
        .status-time {
            font-size: 0.72rem;
            color: #596577;
            margin-top: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# Fetch live data
df = get_dashboard_data()

if not df.empty:
    current_data = df.iloc[-1]
    gateway_online = get_gateway_status(current_data)
else:
    current_data = {'Temperature (°C)': 0, 'AQI (MQ-135)': 0, 'Noise Level (dB)': 0,
                    'status_n1': 'OFF', 'status_n2': 'OFF', 'status_n3': 'OFF'}
    gateway_online = False

# Gateway status
fog_status_text = "🟢 GATEWAY ONLINE" if gateway_online else "🔴 GATEWAY OFFLINE"
fog_status_color = "#00FFAA" if gateway_online else "#FF4B4B"

# Node status flags
n1_offline = current_data.get('status_n1') == 'OFF'
n2_offline = current_data.get('status_n2') == 'OFF'
n3_offline = current_data.get('status_n3') == 'OFF'

# ── Temperature ──────────────────────────────────────────────────────────────
if n1_offline:
    t_val_html = '<span style="color:#FF4B4B; font-size:1.6rem; font-weight:800;">OFFLINE</span>'
    t_sub = '<span style="color:#FF4B4B;">Check sensor power</span>'
    t_color = "#FF4B4B"
else:
    temp = current_data['Temperature (°C)']
    t_color = "#00FFAA" if temp <= THRESHOLDS['temp'] else "#FF4B4B"
    t_val_html = f'<span style="color:{t_color}; font-size:2rem; font-weight:800;">{temp:.1f}<span style="font-size:1rem; color:#7C8FAC;"> °C</span></span>'
    t_sub = f'<span style="color:#596577;">Limit: {THRESHOLDS["temp"]} °C</span>'

# ── AQI ───────────────────────────────────────────────────────────────────────
aqi_val = current_data['AQI (MQ-135)']
aqi_over = not n2_offline and aqi_val > THRESHOLDS['aqi']
a_border_color = '#FF4B4B' if (n2_offline or aqi_over) else 'rgba(255,255,255,0.09)'

if n2_offline:
    a_val_html = '<span style="color:#FF4B4B; font-size:1.6rem; font-weight:800;">OFFLINE</span>'
    a_sub = '<span style="color:#FF4B4B;">Check sensor power</span>'
    a_warning = ""
else:
    a_color = "#FF4B4B" if aqi_over else "#00FFAA"
    a_val_html = f'<span style="color:{a_color}; font-size:2rem; font-weight:800;">{aqi_val:.0f}<span style="font-size:1rem; color:#7C8FAC;"> AQI</span></span>'
    a_sub = f'<span style="color:#596577;">Limit: {THRESHOLDS["aqi"]} AQI</span>'
    a_warning = '<div class="m-warning">⚠ Elevated levels detected</div>' if aqi_over else ""

# ── Sound ─────────────────────────────────────────────────────────────────────
noise_val = current_data['Noise Level (dB)']
noise_over = not n3_offline and noise_val > THRESHOLDS['noise']

if n3_offline:
    n_val_html = '<span style="color:#FF4B4B; font-size:1.6rem; font-weight:800;">OFFLINE</span>'
    n_sub = '<span style="color:#596577;">Check sensor power</span>'
    n_warning = ""
else:
    n_color = "#FF4B4B" if noise_over else "#A78BFA"
    n_val_html = f'<span style="color:{n_color}; font-size:2rem; font-weight:800;">{noise_val:.1f}<span style="font-size:1rem; color:#7C8FAC;"> dB</span></span>'
    n_sub = f'<span style="color:#596577;">Limit: {THRESHOLDS["noise"]} dB</span>'
    n_warning = '<div class="m-warning">⚠ Elevated noise detected</div>' if noise_over else ""

from datetime import datetime
now_str = datetime.now().strftime('%H:%M:%S')

# ── Render ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
    <h2>ComplianceNet Pro</h2>
    <div class="subtitle">Industrial Environmental Compliance Monitoring Network</div>
</div>

<div class="m-card {'offline' if n1_offline else ''}">
    <div class="m-card-label">🌡️ Temperature</div>
    {t_val_html}
    <div class="m-card-sub">{t_sub}</div>
</div>

<div class="m-card {'offline' if n2_offline else ''}" style="border-left: 3px solid {a_border_color};">
    <div class="m-card-label">💨 AQI</div>
    {a_val_html}
    <div class="m-card-sub">{a_sub}</div>
    {a_warning}
</div>

<div class="m-card {'offline' if n3_offline else ''}">
    <div class="m-card-label">🔊 Sound in dB</div>
    {n_val_html}
    <div class="m-card-sub">{n_sub}</div>
    {n_warning}
</div>

<div class="status-badge">
    <div class="status-text" style="color:{fog_status_color};">{fog_status_text}</div>
    <div class="status-time">Last sync: {now_str}</div>
</div>
""", unsafe_allow_html=True)

# ── Mini trend charts ─────────────────────────────────────────────────────────
if not df.empty and len(df) > 1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.82rem; color:#7C8FAC; text-transform:uppercase;
       letter-spacing:1.5px; margin:0 0 8px 0; font-weight:600;">
       Recent Trends
    </p>""", unsafe_allow_html=True)

    mini_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.02)',
        font_color='#E0E6ED',
        margin=dict(l=4, r=4, t=4, b=4),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, showticklabels=True, tickfont=dict(size=9)),
        height=130,
        showlegend=False
    )

    # Temperature mini-chart
    st.markdown('<p style="font-size:0.78rem; color:#A0AEC0; margin:6px 0 2px 0;">🌡️ Temperature (°C)</p>', unsafe_allow_html=True)
    fig_t = go.Figure(go.Scatter(x=df['Timestamp'], y=df['Temperature (°C)'],
                                  mode='lines', line=dict(color='#00FFAA', width=1.8),
                                  fill='tozeroy', fillcolor='rgba(0,255,170,0.07)'))
    fig_t.update_layout(**mini_layout)
    st.plotly_chart(fig_t, use_container_width=True)

    # AQI mini-chart
    st.markdown('<p style="font-size:0.78rem; color:#A0AEC0; margin:6px 0 2px 0;">💨 AQI</p>', unsafe_allow_html=True)
    fig_a = go.Figure(go.Scatter(x=df['Timestamp'], y=df['AQI (MQ-135)'],
                                  mode='lines', line=dict(color='#FF4B4B', width=1.8),
                                  fill='tozeroy', fillcolor='rgba(255,75,75,0.07)'))
    fig_a.update_layout(**mini_layout)
    st.plotly_chart(fig_a, use_container_width=True)

    # Sound mini-chart
    st.markdown('<p style="font-size:0.78rem; color:#A0AEC0; margin:6px 0 2px 0;">🔊 Sound in dB</p>', unsafe_allow_html=True)
    fig_n = go.Figure(go.Scatter(x=df['Timestamp'], y=df['Noise Level (dB)'],
                                  mode='lines', line=dict(color='#A78BFA', width=1.8),
                                  fill='tozeroy', fillcolor='rgba(167,139,250,0.07)'))
    fig_n.update_layout(**mini_layout)
    st.plotly_chart(fig_n, use_container_width=True)