import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import requests
import time

FIREBASE_URL = "https://compliancenet-9cc51-default-rtdb.asia-southeast1.firebasedatabase.app/sensor_logs.json"

# --- SYNCHRONIZED THRESHOLDS (Must match your Pico W exactly) ---
THRESHOLDS = {
    "temp": 35.0,
    "aqi": 150.0,
    "noise": 80.0
}

def get_custom_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .main { background-color: #0E1117; color: #E0E6ED; }
        h1, h2, h3 { color: #E0E6ED; font-family: 'Inter', sans-serif; }

        /* ── Metric Cards ────────────────────────────────── */
        .metric-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
            border-radius: 16px;
            padding: 28px 24px;
            border: 1px solid rgba(255,255,255,0.09);
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
            position: relative;
            overflow: hidden;
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #00FFAA, #00BFFF);
            opacity: 0.7;
            border-radius: 16px 16px 0 0;
        }
        .metric-card.offline {
            opacity: 0.38;
            filter: grayscale(100%);
            border: 1px dashed rgba(255,75,75,0.6);
        }
        .metric-card.offline::before { display: none; }
        .metric-card:not(.offline):hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 40px rgba(0,0,0,0.45);
            border-color: rgba(0,255,170,0.25);
        }
        .metric-value {
            font-size: 2.4rem;
            font-weight: 800;
            color: #00FFAA;
            margin: 12px 0 8px 0;
            line-height: 1.1;
        }
        .metric-label {
            font-size: 0.85rem;
            color: #7C8FAC;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
        }

        /* ── SDG Chips ───────────────────────────────────── */
        .sdg-chip {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 700;
            margin-right: 12px;
            margin-bottom: 12px;
            font-size: 0.9rem;
            transition: all 0.25s ease;
        }
        .sdg-chip:hover { filter: brightness(1.2); cursor: pointer; transform: translateY(-2px); }
        .sdg-3  { background-color: rgba(76,159,56,0.12);   border: 2px solid #4C9F38; color: #4C9F38; }
        .sdg-9  { background-color: rgba(253,105,37,0.12);  border: 2px solid #FD6925; color: #FD6925; }
        .sdg-11 { background-color: rgba(253,157,36,0.12);  border: 2px solid #FD9D24; color: #FD9D24; }
        .sdg-12 { background-color: rgba(191,139,46,0.12);  border: 2px solid #BF8B2E; color: #BF8B2E; }
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

def get_gateway_status(current_data):
    """Monitors the explicit Pico W heartbeat to detect connection loss."""
    if current_data is None or 'heartbeat' not in current_data:
        return False
        
    hb = current_data.get('heartbeat', 0)
    
    if 'last_heartbeat' not in st.session_state:
        st.session_state.last_heartbeat = hb
        st.session_state.last_hb_time = time.time()
        
    if hb != st.session_state.last_heartbeat:
        st.session_state.last_heartbeat = hb
        st.session_state.last_hb_time = time.time()
        
    return (time.time() - st.session_state.last_hb_time) <= 15

def generate_audit_report_pdf(df, current_data, gateway_online):
    """Generate a real, openable PDF audit report using fpdf2."""
    from fpdf import FPDF

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # ── Helpers ────────────────────────────────────────────────────────────────
    DARK_BG    = (14, 17, 23)
    CARD_BG    = (30, 35, 46)
    ACCENT     = (0, 220, 150)
    RED        = (255, 75, 75)
    WHITE      = (224, 230, 237)
    MUTED      = (120, 140, 170)
    BORDER     = (45, 52, 68)

    def compliance_status(val, threshold):
        return ("COMPLIANT", ACCENT) if val <= threshold else ("VIOLATION", RED)

    def safe_text(s):
        """Encode to latin-1, replacing any unmappable char with '?'."""
        return str(s).encode("latin-1", errors="replace").decode("latin-1")

    # ── PDF Setup ──────────────────────────────────────────────────────────────
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Background
    pdf.set_fill_color(*DARK_BG)
    pdf.rect(0, 0, 210, 297, 'F')

    # ── Header Banner ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*CARD_BG)
    pdf.rect(0, 0, 210, 38, 'F')
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 38, 210, 2, 'F')

    pdf.set_xy(12, 7)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 10, safe_text("ComplianceNet Pro"), ln=0)

    pdf.set_xy(12, 19)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 6, safe_text("Industrial Environmental Compliance Monitoring Network"), ln=0)

    # Report label top-right
    pdf.set_xy(130, 9)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(68, 6, safe_text("AUDIT REPORT"), align="R", ln=0)
    pdf.set_xy(130, 17)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(68, 5, safe_text(f"Generated: {datetime_str}"), align="R", ln=0)

    # ── Meta Row ───────────────────────────────────────────────────────────────
    pdf.set_xy(12, 46)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    gw_label = "ONLINE" if gateway_online else "OFFLINE"
    gw_color  = ACCENT if gateway_online else RED
    pdf.cell(0, 6, safe_text(f"Reporting Period: {date_str}  |  Records analysed: {len(df)}  |  Gateway: {gw_label}"), ln=1)

    # ── Section: Current Readings ──────────────────────────────────────────────
    pdf.set_xy(12, 58)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 8, safe_text("Current Sensor Readings"), ln=1)

    # Thin accent underline
    pdf.set_fill_color(*ACCENT)
    pdf.rect(12, pdf.get_y(), 186, 0.5, 'F')
    pdf.ln(4)

    sensors = [
        ("Temperature", current_data.get('Temperature (°C)', 0), THRESHOLDS['temp'], "°C", "🌡"),
        ("AQI",         current_data.get('AQI (MQ-135)', 0),     THRESHOLDS['aqi'],  "AQI", "💨"),
        ("Sound",       current_data.get('Noise Level (dB)', 0), THRESHOLDS['noise'], "dB", "🔊"),
    ]

    col_w = 58
    x_start = 12
    y_start = pdf.get_y() + 2

    for i, (label, val, threshold, unit, _icon) in enumerate(sensors):
        x = x_start + i * (col_w + 6)
        status_text, status_color = compliance_status(val, threshold)

        # Card background
        pdf.set_fill_color(*CARD_BG)
        pdf.rect(x, y_start, col_w, 36, 'F')

        # Left accent stripe
        pdf.set_fill_color(*status_color)
        pdf.rect(x, y_start, 3, 36, 'F')

        # Label
        pdf.set_xy(x + 6, y_start + 4)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*MUTED)
        pdf.cell(col_w - 8, 5, safe_text(label.upper()), ln=0)

        # Value
        pdf.set_xy(x + 6, y_start + 12)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(*WHITE)
        pdf.cell(col_w - 8, 10, safe_text(f"{val:.1f} {unit}"), ln=0)

        # Threshold line
        pdf.set_xy(x + 6, y_start + 24)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*MUTED)
        pdf.cell(col_w - 8, 5, safe_text(f"Limit: {threshold} {unit}"), ln=0)

        # Status badge
        pdf.set_xy(x + 6, y_start + 30)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*status_color)
        pdf.cell(col_w - 8, 4, safe_text(status_text), ln=0)

    pdf.set_y(y_start + 44)

    # ── Section: Compliance Summary ────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.set_x(12)
    pdf.cell(0, 8, safe_text("Compliance Summary"), ln=1)
    pdf.set_fill_color(*ACCENT)
    pdf.rect(12, pdf.get_y(), 186, 0.5, 'F')
    pdf.ln(4)

    if not df.empty:
        over_temp  = int((df['Temperature (°C)'] > THRESHOLDS['temp']).sum())
        over_aqi   = int((df['AQI (MQ-135)']     > THRESHOLDS['aqi']).sum())
        over_noise = int((df['Noise Level (dB)']  > THRESHOLDS['noise']).sum())
        total      = len(df)

        summary_rows = [
            ("Temperature",  over_temp,  total, THRESHOLDS['temp'],   "°C"),
            ("AQI",          over_aqi,   total, THRESHOLDS['aqi'],    "AQI"),
            ("Sound Level",  over_noise, total, THRESHOLDS['noise'],  "dB"),
        ]

        # Table header
        pdf.set_x(12)
        pdf.set_fill_color(*BORDER)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*MUTED)
        pdf.cell(50, 7, "Parameter",        fill=True, border=0, ln=0)
        pdf.cell(35, 7, "Threshold",        fill=True, border=0, ln=0)
        pdf.cell(35, 7, "Violations",       fill=True, border=0, ln=0)
        pdf.cell(35, 7, "Compliance Rate",  fill=True, border=0, ln=0)
        pdf.cell(31, 7, "Status",           fill=True, border=0, ln=1)

        for param, violations, total_r, threshold, unit in summary_rows:
            rate = 100 * (total_r - violations) / total_r if total_r > 0 else 100
            s_text, s_color = ("PASS", ACCENT) if violations == 0 else ("FAIL", RED)

            pdf.set_x(12)
            pdf.set_fill_color(*CARD_BG)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*WHITE)
            pdf.cell(50, 7, param, fill=True, border=0, ln=0)
            pdf.cell(35, 7, f"{threshold} {unit}", fill=True, border=0, ln=0)
            pdf.cell(35, 7, f"{violations} / {total_r}", fill=True, border=0, ln=0)
            pdf.cell(35, 7, f"{rate:.1f}%", fill=True, border=0, ln=0)

            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*s_color)
            pdf.cell(31, 7, s_text, fill=True, border=0, ln=1)

        # Thin separator rows
        pdf.set_fill_color(*BORDER)
        pdf.rect(12, pdf.get_y(), 186, 0.3, 'F')

    pdf.ln(6)

    # ── Section: Data Log ──────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.set_x(12)
    pdf.cell(0, 8, "Sensor Data Log (Last 20 Records)", ln=1)
    pdf.set_fill_color(*ACCENT)
    pdf.rect(12, pdf.get_y(), 186, 0.5, 'F')
    pdf.ln(4)

    if not df.empty:
        log_df = df.tail(20).copy()
        if 'Timestamp' in log_df.columns:
            log_df['Timestamp'] = log_df['Timestamp'].dt.strftime('%H:%M:%S')

        # Header
        pdf.set_x(12)
        pdf.set_fill_color(*BORDER)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(42, 6, "Timestamp",       fill=True, border=0, ln=0)
        pdf.cell(48, 6, "Temperature (°C)",fill=True, border=0, ln=0)
        pdf.cell(48, 6, "AQI",             fill=True, border=0, ln=0)
        pdf.cell(48, 6, "Sound (dB)",      fill=True, border=0, ln=1)

        for _, row in log_df.iterrows():
            ts   = str(row.get('Timestamp', '—'))
            temp = row.get('Temperature (°C)', 0)
            aqi  = row.get('AQI (MQ-135)', 0)
            snd  = row.get('Noise Level (dB)', 0)

            pdf.set_x(12)
            pdf.set_fill_color(*CARD_BG)
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(*WHITE)
            pdf.cell(42, 5.5, ts, fill=True, border=0, ln=0)

            # Temp cell
            t_col = RED if temp > THRESHOLDS['temp'] else WHITE
            pdf.set_text_color(*t_col)
            pdf.cell(48, 5.5, f"{temp:.1f}", fill=True, border=0, ln=0)

            # AQI cell
            a_col = RED if aqi > THRESHOLDS['aqi'] else WHITE
            pdf.set_text_color(*a_col)
            pdf.cell(48, 5.5, f"{aqi:.0f}", fill=True, border=0, ln=0)

            # Noise cell
            n_col = RED if snd > THRESHOLDS['noise'] else WHITE
            pdf.set_text_color(*n_col)
            pdf.cell(48, 5.5, f"{snd:.1f}", fill=True, border=0, ln=1)

        pdf.set_fill_color(*BORDER)
        pdf.rect(12, pdf.get_y(), 186, 0.3, 'F')

    # ── Footer ─────────────────────────────────────────────────────────────────
    pdf.set_y(277)
    pdf.set_fill_color(*CARD_BG)
    pdf.rect(0, 275, 210, 22, 'F')
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 275, 210, 0.5, 'F')

    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 5,
             safe_text(f"ComplianceNet Pro  |  Auto-generated report  |  {datetime_str}  |  "
                       "For regulatory use only - verify against primary sensor logs."),
             align="C", ln=0)

    return bytes(pdf.output())