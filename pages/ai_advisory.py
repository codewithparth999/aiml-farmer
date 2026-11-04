import streamlit as st
import requests
from datetime import datetime

from services.advisory_engine import generate_irrigation_advisory
from services.database import (
    save_report,
    get_fields,
    get_crop_configurations
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Irrigation Advisory | AIML FARMER",
    page_icon="💧",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# MASTER UI THEME
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0B1711;
    color: #E8F5EA;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    color: #E8F5EA !important;
}

p, label, span {
    color: #D1E7D6;
}

/* Metric Cards */

[data-testid="stMetric"] {
    background: #142D20;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #315C3D;
}

[data-testid="stMetricLabel"] {
    color: #A7C9AE !important;
}

[data-testid="stMetricValue"] {
    color: #E8F5EA !important;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #0E1F16;
}

/* Input Fields */

.stTextInput input,
.stNumberInput input {
    background-color: #142D20 !important;
    color: #E8F5EA !important;
    border: 1px solid #315C3D !important;
    border-radius: 8px !important;
}

/* Select Boxes */

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #142D20;
    border-color: #315C3D;
    color: #E8F5EA;
}

/* Buttons */

.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(90deg, #15803D, #16A34A);
    color: white !important;
    border: none;
    border-radius: 9px;
    font-weight: 600;
    padding: 10px 18px;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    border: 1px solid #86EFAC;
    color: white !important;
}

/* Containers */

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #10251A;
    border: 1px solid #315C3D;
    border-radius: 14px;
    padding: 10px;
}

/* Divider */

hr {
    border-color: #315C3D;
}

/* Hero */

.hero-box {
    background: linear-gradient(120deg, #0E2A1A, #14532D, #166534);
    padding: 30px;
    border-radius: 18px;
    border: 1px solid #347A4B;
    margin-bottom: 25px;
}

.hero-tag {
    color: #86EFAC;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero-title {
    color: #F0FDF4;
    font-size: 36px;
    font-weight: 800;
    margin-top: 8px;
}

.hero-subtitle {
    color: #C7E9D0;
    font-size: 15px;
    margin-top: 8px;
}

.section-label {
    color: #86EFAC;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero-box">
    <div class="hero-tag">SMART AGRICULTURE INTELLIGENCE PLATFORM</div>
    <div class="hero-title">💧 AI Irrigation Advisory</div>
    <div class="hero-subtitle">
        Intelligent irrigation recommendations using field,
        crop, soil and weather information.
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD SAVED DATA
# --------------------------------------------------

st.markdown(
    '<div class="section-label">SAVED FARM CONFIGURATION</div>',
    unsafe_allow_html=True
)

st.subheader("🌾 Saved Farm Data")

saved_fields = get_fields()
saved_configs = get_crop_configurations()

field_options = {}

if saved_fields:

    field_options = {
        f'{f["field_name"]} | {f["area"]} ha': f
        for f in saved_fields
    }

    selected_field = st.selectbox(
        "Select Registered Field",
        ["Manual Entry"] + list(field_options.keys())
    )

else:

    selected_field = "Manual Entry"

    st.info("No registered fields found.")

config_options = {}
selected_config = None

if saved_configs:

    config_options = {
        f'{c["crop"]} | {c["soil_type"]} | {c["field_area"]} ha': c
        for c in saved_configs
    }

    selected_config_name = st.selectbox(
        "Load Saved Crop & Soil Configuration",
        ["Manual Entry"] + list(config_options.keys())
    )

    if selected_config_name != "Manual Entry":
        selected_config = config_options[selected_config_name]


# --------------------------------------------------
# DEFAULT VALUES
# --------------------------------------------------

default_area = 2.0
default_crop = "Wheat"
default_fc = 30.0
default_wp = 12.0
default_root = 1.0

supported_crops = [
    "Wheat",
    "Rice",
    "Maize",
    "Mustard",
    "Tomato"
]

if selected_field != "Manual Entry":

    field_data = field_options[selected_field]

    default_area = float(field_data["area"])

    if field_data.get("crop") in supported_crops:
        default_crop = field_data["crop"]

if selected_config:

    default_area = float(selected_config["field_area"])
    default_crop = selected_config["crop"]
    default_fc = float(selected_config["field_capacity"])
    default_wp = float(selected_config["wilting_point"])
    default_root = float(selected_config["root_depth"])

if default_crop not in supported_crops:
    default_crop = "Wheat"


# --------------------------------------------------
# FIELD INPUTS
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-label">FIELD CONFIGURATION</div>',
    unsafe_allow_html=True
)

st.subheader("🌱 Field & Crop Information")

col1, col2 = st.columns(2)

with col1:

    st.markdown("#### 🌾 Field Details")

    field_area = st.number_input(
        "Field Area (hectares)",
        min_value=0.1,
        max_value=1000.0,
        value=default_area,
        key="advisory_area"
    )

    crop = st.selectbox(
        "Select Crop",
        supported_crops,
        index=supported_crops.index(default_crop),
        key="advisory_crop"
    )

    root_depth = st.number_input(
        "Root Depth (m)",
        min_value=0.1,
        max_value=3.0,
        value=default_root,
        key="advisory_root"
    )

with col2:

    st.markdown("#### 💧 Soil Conditions")

    field_capacity = st.number_input(
        "Field Capacity (%)",
        min_value=1.0,
        max_value=100.0,
        value=default_fc,
        key="advisory_fc"
    )

    wilting_point = st.number_input(
        "Wilting Point (%)",
        min_value=0.0,
        max_value=99.0,
        value=default_wp,
        key="advisory_wp"
    )

    current_moisture = st.number_input(
        "Current Soil Moisture (%)",
        min_value=0.0,
        max_value=100.0,
        value=22.0
    )


# --------------------------------------------------
# WEATHER INPUTS
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-label">WEATHER PARAMETERS</div>',
    unsafe_allow_html=True
)

st.subheader("🌦️ Weather Information")

weather_col1, weather_col2 = st.columns(2)

with weather_col1:

    et0 = st.number_input(
        "Reference ET0 (mm/day)",
        min_value=0.0,
        max_value=20.0,
        value=4.0
    )

with weather_col2:

    forecast_rain = st.number_input(
        "Expected Rainfall (mm)",
        min_value=0.0,
        max_value=200.0,
        value=0.0
    )


# --------------------------------------------------
# CROP COEFFICIENT
# --------------------------------------------------

kc_values = {
    "Wheat": 1.15,
    "Rice": 1.10,
    "Maize": 1.20,
    "Mustard": 1.00,
    "Tomato": 1.15
}

st.info(
    f"🌱 Selected Crop: **{crop}** | "
    f"Crop Coefficient (Kc): **{kc_values[crop]}**"
)


# --------------------------------------------------
# GENERATE ADVISORY THROUGH BACKEND
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-label">IRRIGATION INTELLIGENCE</div>',
    unsafe_allow_html=True
)

st.subheader("🤖 Generate Irrigation Recommendation")

if st.button(
    "🚀 Generate AI Advisory",
    use_container_width=True
):

    if field_capacity <= wilting_point:

        st.error("Field Capacity must be greater than Wilting Point.")

    elif not (
        wilting_point <= current_moisture <= field_capacity
    ):

        st.error(
            "Current Soil Moisture must be between "
            "Wilting Point and Field Capacity."
        )

    else:

        try:

            with st.spinner("Connecting to FastAPI backend..."):

                # Saved configuration: use FastAPI
                if selected_config:

                    payload = {
                        "field_id": selected_config["id"],
                        "current_moisture": current_moisture,
                        "et0": et0,
                        "forecast_rain": forecast_rain
                    }

                    response = requests.post(
                        f"{API_URL}/advisory",
                        json=payload,
                        timeout=20
                    )

                    response.raise_for_status()

                    api_response = response.json()

                    result = api_response.get(
                        "advisory",
                        api_response
                    )

                    st.session_state["advisory_source"] = "FastAPI Backend"

                else:

                    # Manual entry: existing Python advisory engine
                    result = generate_irrigation_advisory(
                        field_capacity=field_capacity,
                        wilting_point=wilting_point,
                        current_moisture=current_moisture,
                        root_depth=root_depth,
                        et0=et0,
                        crop_coefficient=kc_values[crop],
                        depletion_fraction=0.55,
                        field_area=field_area,
                        forecast_rain=forecast_rain
                    )

                    st.session_state["advisory_source"] = "Local Python Engine"

            st.session_state["ai_advisory_result"] = result

            st.session_state["ai_advisory_inputs"] = {
                "crop": crop,
                "field_area": field_area
            }

            st.success("Advisory generated successfully!")

        except requests.exceptions.ConnectionError:

            st.error(
                "Backend connection failed. Start FastAPI first."
            )

        except requests.exceptions.HTTPError as error:

            st.error(f"Backend API error: {error}")

            try:
                st.code(response.text)
            except Exception:
                pass

        except ValueError as error:

            st.error(str(error))

        except Exception as error:

            st.error(f"Unable to generate advisory: {error}")


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "ai_advisory_result" in st.session_state:

    result = st.session_state["ai_advisory_result"]

    advisory_inputs = st.session_state.get(
        "ai_advisory_inputs",
        {
            "crop": crop,
            "field_area": field_area
        }
    )

    result_crop = advisory_inputs["crop"]
    result_area = advisory_inputs["field_area"]

    st.divider()

    st.markdown(
        '<div class="section-label">GENERATED RESULTS</div>',
        unsafe_allow_html=True
    )

    st.subheader("📊 Irrigation Recommendation")

    st.caption(
        f"Generated through: "
        f"{st.session_state.get('advisory_source', 'Python Engine')}"
    )

    decision = result.get("decision", "UNKNOWN")

    if decision == "IRRIGATE NOW":
        st.error("💧 IRRIGATION REQUIRED")

    elif decision == "MONITOR":
        st.warning("👀 MONITOR SOIL MOISTURE")

    else:
        st.success("✅ IRRIGATION NOT REQUIRED YET")

    st.write(
        result.get(
            "reason",
            "No additional explanation available."
        )
    )

    # --------------------------------------------------
    # WATER ANALYSIS
    # --------------------------------------------------

    st.divider()

    st.subheader("🌱 Crop Water Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Crop Water Requirement",
        f'{result["etc_mm_day"]} mm/day'
    )

    col2.metric(
        "Soil Water Depletion",
        f'{result["adjusted_depletion_mm"]} mm'
    )

    col3.metric(
        "Available Water",
        f'{result["total_available_water_mm"]} mm'
    )

    # --------------------------------------------------
    # IRRIGATION REQUIREMENT
    # --------------------------------------------------

    st.divider()

    st.subheader("💧 Irrigation Water Requirement")

    col1, col2 = st.columns(2)

    col1.metric(
        "Net Irrigation",
        f'{result["net_irrigation_mm"]} mm'
    )

    col2.metric(
        "Gross Irrigation",
        f'{result["gross_irrigation_mm"]} mm'
    )

    st.metric(
        "Estimated Water Volume",
        f'{result["water_required_liters"]:,.0f} Liters'
    )

    st.caption(
        f"Crop: {result_crop} | "
        f"Field Area: {result_area} hectares"
    )

    # --------------------------------------------------
    # SAVE REPORT
    # --------------------------------------------------

    st.divider()

    st.subheader("💾 Save Advisory Report")

    if st.button(
        "💾 Save Advisory to Database",
        use_container_width=True
    ):

        try:

            report = {
                "Date & Time": datetime.now().strftime(
                    "%d-%m-%Y %H:%M"
                ),
                "Crop": result_crop,
                "Field Area (ha)": result_area,
                "Decision": result["decision"],
                "Crop Water Requirement (mm/day)": result["etc_mm_day"],
                "Soil Water Depletion (mm)": result["adjusted_depletion_mm"],
                "Available Water (mm)": result["total_available_water_mm"],
                "Net Irrigation (mm)": result["net_irrigation_mm"],
                "Gross Irrigation (mm)": result["gross_irrigation_mm"],
                "Water Required (Liters)": result["water_required_liters"]
            }

            save_report(report)

            st.success("Advisory saved successfully!")

        except Exception as error:

            st.error(f"Unable to save advisory: {error}")

    st.warning(
        "⚠️ This advisory is an estimate based on entered values. "
        "Verify actual field conditions before making irrigation decisions."
    )

else:

    st.info(
        "Enter field details and generate your irrigation recommendation. "
        "Your results will appear here."
    )
    