# 🏭 ComplianceNet Pro - Industrial Environmental Monitoring Network

An end-to-end, distributed compliance monitoring network designed for rapid deployment in industrial and factory environments. This system ensures continuous logging and regulatory adherence regarding ambient air quality (gases), noise levels, and ambient working temperatures.

## 🌟 Overview & Regulatory Compliance

This monitoring dashboard pairs with a Zigbee-based sensor array. In many regions, regulatory bodies and auditors require verifiable, continuous logs to ensure compliance. Failure to comply often results in shutdowns or heavy fines. 

**This network directly targets UN Sustainable Development Goals (SDGs):**
- **SDG 3**: Good Health & Well-Being (protecting workers from hazardous noises and gases)
- **SDG 9**: Industry & Infrastructure (retrofitting legacy factories with wireless IoT)
- **SDG 11**: Sustainable Cities (preventing toxic factory gas leaks from impacting local communities)
- **SDG 12**: Responsible Production (verifiable, responsible chemical and emissions management)

---

## ⚙️ Hardware Architecture

The physical network consists of **3 Edge Sensor Nodes** and **1 Collector Node**, all communicating via an industrially robust, self-healing **Zigbee Wireless Mesh**.

### 1. Edge Sensor Nodes (STM32 / RP2040)
The microcontrollers on the factory floor interface directly with:
- **MQ-135 Gas Sensors**: Detects broad-spectrum hazardous gases (CO2, NH3, Benzene).
- **KY-038 Sound Sensors**: Monitors occupational noise safety (Acoustics in dB).
- **DHT11 Sensors**: Measures ambient working conditions (Temperature).

### 2. Collector Node & Main Microcontroller
A central collector gathers data from the 3 Zigbee sensor nodes. A main microcontroller processes, timestamps, validates, and securely pushes this data to the Cloud/AI APIs to drive this very dashboard.

---

## 💻 Software Features (The Dashboards)

This project contains **two** native interfaces built entirely in Python using Streamlit:

### 1. `cps_dash.py` (Main Regulatory Web Dashboard)
A command center for managers and auditors.
- Real-time visualizations of Air Quality, Noise, and Temperature.
- Embedded AI-based trend detection for early warning alerts.
- One-click generated continuous PDF compliance logs for auditing.
- Dedicated hardware architectural and SDG compliance informational tabs.

### 2. `mobile_app.py` (Field Engineer Mobile View)
A specialized, mobile-optimized standalone application.
- Native mobile layout and sizing constraints.
- Real-time on-floor data viewing for roaming engineers.
- Embedded sync controls for local mesh network interactions.

---

## 🚀 How to Run & Deploy to Streamlit Community Cloud

This project is built using `Streamlit` and configured specifically for free cloud deployment via **Streamlit Community Cloud**.

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run Main Dashboard (usually opens on port 8501)
streamlit run cps_dash.py

# Run Mobile App locally (specify a different port, like 8502)
streamlit run mobile_app.py --server.port 8502
```

### Free Cloud Deployment Steps

Host this live so managers, field engineers, and auditors can access it via a URL anywhere in the world!

1. **Upload to GitHub**: Create a free GitHub account and make a new repository. Upload all 4 files: `cps_dash.py`, `mobile_app.py`, `utils.py`, and `requirements.txt`.
2. **Access Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io/) and select "Continue with GitHub".
3. **Deploy the Main Dashboard**: 
   - Click **New App**.
   - Select your new repository.
   - For the "Main file path", type `cps_dash.py`.
   - Click Deploy!
4. **Deploy the Mobile App**:
   - Go back to [share.streamlit.io](https://share.streamlit.io/).
   - Click **New App** again.
   - Select the exact same repository.
   - For the "Main file path", type `mobile_app.py`.
   - Click Deploy!

You now have two active URLs running your distinct dashboards directly from the cloud for free!
