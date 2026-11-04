import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def get_api_data(endpoint):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}"
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Backend Error: {e}")
        return None

import requests
import streamlit as st

from services.advisory_engine import generate_irrigation_advisory
from services.database import (
    get_fields,
    get_crop_configurations,
    save_report
)

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AIML FARMER",
    page_icon="🌱",
    layout="wide"
)

# GLOBAL THEME
st.markdown("""
<style>
.stApp {
    background-color: #0B1711;
    color: #E8F5EA;
}
[data-testid="stMetric"] {
    background: #142D20;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #315C3D;
}
h1, h2, h3 {
    color: #E8F5EA;
}
[data-testid="stSidebar"] {
    background-color: #0E1F16;
}
</style>
""", unsafe_allow_html=True)


# HERO SECTION

st.markdown("""
<div style="background:linear-gradient(115deg,#0D261B,#153B29,#1C5034);border:1px solid #34704A;border-radius:20px;padding:32px 30px;margin-bottom:24px;">
<div style="color:#91D6A5;font-size:11px;font-weight:800;letter-spacing:2.5px;">SMART AGRICULTURE INTELLIGENCE PLATFORM</div>
<div style="color:#F2FFF5;font-size:36px;font-weight:850;margin-top:12px;">🌱 AIML FARMER</div>
<div style="color:#D4EBDD;font-size:19px;font-weight:600;margin-top:7px;">AI-Powered Precision Irrigation</div>
<div style="color:#B4CDBB;font-size:14px;margin-top:12px;max-width:750px;line-height:1.7;">Transform field data into intelligent irrigation decisions using soil moisture analysis, crop water requirements and weather-based insights.</div>
<div style="background:#244C35;border:1px solid #477B55;border-radius:9px;padding:9px 13px;display:inline-block;margin-top:17px;color:#B8E8C5;font-size:12px;font-weight:700;">💧 SMART WATER MANAGEMENT &nbsp; • &nbsp; 🌾 CROP INTELLIGENCE</div>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<style>
div[data-testid="stImage"] img {
    height: 300px;
    width: 10%;
    object-fit: cover;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.image("assets/farm_hero.jpg", use_container_width=True)

# LOAD DATABASE RECORDS
fields = get_fields() or []
configurations = get_crop_configurations() or []

# FETCH LIVE DASHBOARD STATISTICS
dashboard_data = None

try:
    dashboard_response = requests.get(
        f"{API_URL}/dashboard-summary",
        timeout=5
    )

    dashboard_response.raise_for_status()
    dashboard_payload = dashboard_response.json()

    dashboard_data = (
        dashboard_payload.get("summary")
        if isinstance(dashboard_payload, dict)
        else None
    )

except (requests.RequestException, ValueError) as error:
    st.warning(f"Dashboard API unavailable: {error}")


# LIVE FARM OVERVIEW
if isinstance(dashboard_data, dict):

    st.markdown("""
<div style="margin:25px 0 15px 0;">
<div style="color:#91C9A0;font-size:11px;font-weight:800;letter-spacing:1.8px;">FARM ANALYTICS</div>
<div style="color:#E8F5EA;font-size:24px;font-weight:800;margin-top:6px;">📊 Live Farm Overview</div>
<div style="color:#B8CDBE;font-size:13px;margin-top:5px;">Real-time statistics from your agriculture database.</div>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("🌾", "TOTAL FIELDS", dashboard_data.get("total_fields", 0)),
        ("🌱", "CROP PROFILES", dashboard_data.get("total_crop_configurations", 0)),
        ("💧", "SOIL READINGS", dashboard_data.get("total_soil_readings", 0)),
        ("📑", "SAVED REPORTS", dashboard_data.get("total_reports", 0))
    ]

    for col, (icon, label, value) in zip(
        [col1, col2, col3, col4], metrics
    ):
        with col:
            st.markdown(f"""
<div style="background:linear-gradient(145deg,#142D20,#102219);border:1px solid #315C3D;border-radius:15px;padding:19px 16px;min-height:125px;">
<div style="font-size:23px;">{icon}</div>
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1px;margin-top:10px;">{label}</div>
<div style="color:#F2FFF5;font-size:29px;font-weight:850;margin-top:5px;">{value}</div>
</div>
""", unsafe_allow_html=True)

    st.divider()


# SIDEBAR HEADER
st.sidebar.markdown("""
<div style="background:linear-gradient(135deg,#142D20,#1B4930);border:1px solid #315C3D;border-radius:13px;padding:17px 14px;margin-bottom:18px;">
<div style="color:#91D6A5;font-size:10px;font-weight:800;letter-spacing:1.5px;">AIML FARMER</div>
<div style="color:#F2FFF5;font-size:19px;font-weight:800;margin-top:7px;">🌾 Field Control</div>
<div style="color:#B8CDBE;font-size:11px;margin-top:5px;">Configure your farm parameters</div>
</div>
""", unsafe_allow_html=True)


# SELECT REGISTERED FIELD
field_options = ["Manual Entry"] + [
    f"{field['field_name']} (ID: {field['id']})"
    for field in fields
]

selected_field = st.sidebar.selectbox(
    "Select Registered Field",
    field_options
)

selected_field_data = None

if selected_field != "Manual Entry":
    selected_index = field_options.index(selected_field) - 1
    selected_field_data = fields[selected_index]


# MATCH CROP CONFIGURATION
matching_configs = []

if selected_field_data:
    matching_configs = [
        config for config in configurations
        if config["crop"] == selected_field_data["crop"]
    ]

config_options = ["Manual Soil Parameters"] + [
    f"{config['crop']} - {config['growth_stage']} (ID: {config['id']})"
    for config in matching_configs
]

selected_config = st.sidebar.selectbox(
    "Select Crop-Soil Configuration",
    config_options
)

config_data = None

if selected_config != "Manual Soil Parameters":
    config_index = config_options.index(selected_config) - 1
    config_data = matching_configs[config_index]


# FIELD AREA
default_area = (
    float(selected_field_data["area"])
    if selected_field_data else 1.0
)

field_area = st.sidebar.number_input(
    "Field Area (hectares)",
    min_value=0.1,
    max_value=1000.0,
    value=default_area
)


# SOIL PARAMETERS SECTION
st.sidebar.markdown("""
<div style="border-top:1px solid #315C3D;padding-top:15px;margin:18px 0 12px 0;">
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1.4px;">SOIL INTELLIGENCE</div>
<div style="color:#E8F5EA;font-size:17px;font-weight:800;margin-top:6px;">💧 Soil Parameters</div>
<div style="color:#B8CDBE;font-size:11px;margin-top:5px;">Define soil water characteristics.</div>
</div>
""", unsafe_allow_html=True)

default_fc = (
    float(config_data["field_capacity"])
    if config_data else 30.0
)

default_wp = (
    float(config_data["wilting_point"])
    if config_data else 12.0
)

default_root = (
    float(config_data["root_depth"])
    if config_data else 1.0
)

field_capacity = st.sidebar.number_input(
    "Field Capacity (%)",
    1.0, 100.0, default_fc
)

wilting_point = st.sidebar.number_input(
    "Wilting Point (%)",
    0.0, 99.0, default_wp
)

current_moisture = st.sidebar.number_input(
    "Current Soil Moisture (%)",
    0.0, 100.0, 22.0
)

root_depth = st.sidebar.number_input(
    "Root Depth (m)",
    0.1, 3.0, default_root
)


# CROP AND WEATHER SECTION
st.sidebar.markdown("""
<div style="border-top:1px solid #315C3D;padding-top:15px;margin:18px 0 12px 0;">
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1.5px;">CROP & CLIMATE</div>
<div style="color:#E8F5EA;font-size:17px;font-weight:800;margin-top:6px;">🌦️ Crop & Weather</div>
<div style="color:#B8CDBE;font-size:11px;margin-top:5px;">Set crop water demand and rainfall.</div>
</div>
""", unsafe_allow_html=True)

crop_coefficient = st.sidebar.number_input(
    "Crop Coefficient (Kc)",
    0.1, 2.0, 1.15
)

et0 = st.sidebar.number_input(
    "Reference ET0 (mm/day)",
    0.0, 20.0, 4.0
)

depletion_fraction = st.sidebar.number_input(
    "Depletion Fraction",
    0.1, 1.0, 0.55
)

forecast_rain = st.sidebar.number_input(
    "Expected Rainfall (mm)",
    0.0, 200.0, 0.0
)

st.sidebar.caption(
    "Use field-measured soil values and verified local weather. "
    "Default values are illustrative."
)


# REGISTERED FIELD INFORMATION
if selected_field_data:

    st.markdown(f"""
<div style="background:linear-gradient(120deg,#142D20,#193B29);border:1px solid #315C3D;border-radius:15px;padding:20px 22px;margin:20px 0;">
<div style="color:#91D6A5;font-size:10px;font-weight:800;letter-spacing:1.6px;">ACTIVE FIELD PROFILE</div>
<div style="color:#F2FFF5;font-size:22px;font-weight:800;margin-top:8px;">🌾 {selected_field_data['field_name']}</div>
<div style="display:flex;flex-wrap:wrap;gap:24px;margin-top:17px;">
<div><div style="color:#91C9A0;font-size:10px;font-weight:700;">CROP</div><div style="color:#E8F5EA;font-size:14px;font-weight:600;margin-top:4px;">{selected_field_data['crop']}</div></div>
<div><div style="color:#91C9A0;font-size:10px;font-weight:700;">SOIL TYPE</div><div style="color:#E8F5EA;font-size:14px;font-weight:600;margin-top:4px;">{selected_field_data['soil_type']}</div></div>
<div><div style="color:#91C9A0;font-size:10px;font-weight:700;">LOCATION</div><div style="color:#E8F5EA;font-size:14px;font-weight:600;margin-top:4px;">{selected_field_data['location']}</div></div>
</div>
</div>
""", unsafe_allow_html=True)


# EMPTY FIELD STATE
if not fields:
    st.markdown("""
<div style="background:linear-gradient(120deg,#142D20,#193B29);border:1px dashed #477B55;border-radius:15px;padding:22px;margin:20px 0;">
<div style="font-size:28px;">🌱</div>
<div style="color:#F2FFF5;font-size:19px;font-weight:800;margin-top:8px;">Your farm journey starts here</div>
<div style="color:#B8CDBE;font-size:13px;margin-top:7px;line-height:1.6;">No registered fields found. Add your first field through Field Management to unlock personalized irrigation intelligence.</div>
</div>
""", unsafe_allow_html=True)


# GENERATE ADVISORY SECTION
st.markdown("""
<div style="border-top:1px solid #315C3D;padding-top:22px;margin:25px 0 15px 0;">
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1.8px;">AI-POWERED DECISION ENGINE</div>
<div style="color:#E8F5EA;font-size:25px;font-weight:850;margin-top:7px;">🤖 Generate Irrigation Advisory</div>
<div style="color:#B8CDBE;font-size:13px;margin-top:6px;">Analyze soil, crop and weather parameters to generate an irrigation recommendation.</div>
</div>
""", unsafe_allow_html=True)


# GENERATE ADVISORY
if st.button(
    "🌱 GENERATE IRRIGATION ADVISORY",
    use_container_width=True
):

    try:
        if config_data:

            response = requests.post(
                f"{API_URL}/advisory",
                json={
                    "field_id": config_data["id"],
                    "current_moisture": current_moisture,
                    "et0": et0,
                    "forecast_rain": forecast_rain
                },
                timeout=10
            )

            response.raise_for_status()
            result = response.json()["advisory"]

        else:

            result = generate_irrigation_advisory(
                field_capacity=field_capacity,
                wilting_point=wilting_point,
                current_moisture=current_moisture,
                root_depth=root_depth,
                et0=et0,
                crop_coefficient=crop_coefficient,
                depletion_fraction=depletion_fraction,
                field_area=field_area,
                forecast_rain=forecast_rain
            )

        st.session_state["advisory"] = result

        # SAVE ADVISORY IN DATABASE
        save_report({
            "type": "dashboard_advisory",
            "field": (
                selected_field_data["field_name"]
                if selected_field_data else "Manual Entry"
            ),
            "inputs": {
                "field_area": field_area,
                "field_capacity": field_capacity,
                "wilting_point": wilting_point,
                "current_moisture": current_moisture,
                "root_depth": root_depth,
                "et0": et0,
                "crop_coefficient": crop_coefficient,
                "depletion_fraction": depletion_fraction,
                "forecast_rain": forecast_rain
            },
            "result": result
        })

        st.success("Advisory generated and saved successfully!")

    except requests.RequestException as error:
        st.error(f"Backend connection failed: {error}")

    except (ValueError, KeyError) as error:
        st.error(str(error))


# DISPLAY ADVISORY
if "advisory" in st.session_state:

    result = st.session_state["advisory"]

    st.divider()

    st.markdown("""
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1.7px;">SMART FARM DECISION</div>
<div style="color:#E8F5EA;font-size:23px;font-weight:850;margin-top:6px;">🚨 Irrigation Decision</div>
""", unsafe_allow_html=True)

    decision = result["decision"]

    decision_colors = {
        "IRRIGATE NOW": ("#5B2424", "#FF8B8B", "💧"),
        "MONITOR": ("#51401D", "#FFD477", "👀")
    }

    bg, accent, icon = decision_colors.get(
        decision,
        ("#19452C", "#91D6A5", "✅")
    )

    st.markdown(f"""
<div style="background:{bg};border:1px solid {accent};border-radius:16px;padding:22px;margin:18px 0;">
<div style="color:{accent};font-size:10px;font-weight:800;letter-spacing:1.8px;">AI IRRIGATION DECISION</div>
<div style="color:#FFFFFF;font-size:27px;font-weight:850;margin-top:9px;">{icon} {decision}</div>
<div style="color:#F0F5F0;font-size:14px;line-height:1.7;margin-top:12px;">{result["reason"]}</div>
</div>
""", unsafe_allow_html=True)


    # WATER INTELLIGENCE METRICS
    st.markdown("""
<div style="border-top:1px solid #315C3D;padding-top:20px;margin:22px 0 14px 0;">
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1.7px;">SOIL & CROP ANALYTICS</div>
<div style="color:#E8F5EA;font-size:22px;font-weight:850;margin-top:6px;">📊 Water Intelligence Metrics</div>
<div style="color:#B8CDBE;font-size:13px;margin-top:5px;">Key measurements behind your irrigation decision.</div>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    metric_cards = [
        (col1, "🌾", "CROP WATER REQUIREMENT", f'{result["etc_mm_day"]} mm/day'),
        (col2, "💧", "SOIL WATER DEPLETION", f'{result["adjusted_depletion_mm"]} mm'),
        (col3, "🌱", "AVAILABLE WATER (TAW)", f'{result["total_available_water_mm"]} mm')
    ]

    for col, icon, label, value in metric_cards:
        with col:
            st.markdown(f"""
<div style="background:linear-gradient(145deg,#142D20,#102219);border:1px solid #315C3D;border-radius:14px;padding:19px 15px;min-height:125px;">
<div style="font-size:22px;">{icon}</div>
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1px;margin-top:10px;">{label}</div>
<div style="color:#F2FFF5;font-size:23px;font-weight:850;margin-top:7px;">{value}</div>
</div>
""", unsafe_allow_html=True)


    # IRRIGATION WATER REQUIREMENT
    st.markdown("""
<div style="border-top:1px solid #315C3D;padding-top:20px;margin:22px 0 14px 0;">
<div style="color:#91C9A0;font-size:10px;font-weight:800;letter-spacing:1.7px;">PRECISION WATER PLANNING</div>
<div style="color:#E8F5EA;font-size:22px;font-weight:850;margin-top:6px;">💧 Irrigation Water Requirement</div>
<div style="color:#B8CDBE;font-size:13px;margin-top:5px;">Calculated water depth and estimated volume for your field.</div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    col1.metric(
        "Net Irrigation",
        f'{result["net_irrigation_mm"]} mm'
    )

    col2.metric(
        "Gross Irrigation",
        f'{result["gross_irrigation_mm"]} mm'
    )

    # TOTAL WATER VOLUME
    st.markdown(f"""
<div style="background:linear-gradient(115deg,#123B2B,#18543A);border:1px solid #43845A;border-radius:16px;padding:22px;margin:18px 0;">
<div style="color:#A5E6B5;font-size:10px;font-weight:800;letter-spacing:1.7px;">TOTAL ESTIMATED WATER VOLUME</div>
<div style="color:#FFFFFF;font-size:32px;font-weight:900;margin-top:9px;">💧 {result["water_required_liters"]:,.0f} Liters</div>
<div style="color:#C5E5CE;font-size:12px;margin-top:7px;">Estimated irrigation water requirement for the selected field.</div>
</div>
""", unsafe_allow_html=True)

    # AGRICULTURAL DISCLAIMER
    st.markdown("""
<div style="background:#292719;border:1px solid #75602D;border-radius:12px;padding:16px 18px;margin:18px 0;">
<div style="color:#F5D77D;font-size:12px;font-weight:800;letter-spacing:1px;">⚠️ AGRICULTURAL DECISION NOTICE</div>
<div style="color:#E8DFC5;font-size:12px;line-height:1.7;margin-top:8px;">This is an advisory calculation, not a validated farm prescription. Check rainfall effectiveness, soil variability, crop growth stage and local field conditions before irrigation.</div>
</div>
""", unsafe_allow_html=True)


# EMPTY ADVISORY STATE
else:

    st.markdown("""
<div style="background:linear-gradient(120deg,#142D20,#193B29);border:1px dashed #477B55;border-radius:16px;padding:25px;margin:20px 0;">
<div style="font-size:30px;">🤖</div>
<div style="color:#F2FFF5;font-size:20px;font-weight:850;margin-top:10px;">Ready to analyze your field?</div>
<div style="color:#B8CDBE;font-size:13px;line-height:1.7;margin-top:8px;">Select your field or enter soil, crop and weather parameters from the sidebar. Then generate an AI-powered irrigation advisory.</div>
<div style="color:#91D6A5;font-size:11px;font-weight:800;margin-top:15px;">YOUR SMART IRRIGATION JOURNEY STARTS HERE →</div>
</div>
""", unsafe_allow_html=True)


# PREMIUM FOOTER
st.markdown("""
<div style="border-top:1px solid #315C3D;margin-top:35px;padding:20px 5px 10px 5px;text-align:center;">
<div style="color:#91D6A5;font-size:16px;font-weight:850;letter-spacing:1px;">🌱 AIML FARMER</div>
<div style="color:#B8CDBE;font-size:11px;margin-top:7px;">Smart Agriculture Intelligence Platform</div>
<div style="color:#718C79;font-size:10px;margin-top:5px;">Intelligent Irrigation • Sustainable Agriculture • Smarter Water Management</div>
</div>
""", unsafe_allow_html=True)