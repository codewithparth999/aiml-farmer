import streamlit as st
from services.database import save_crop_configuration, get_crop_configurations

st.set_page_config(
    page_title="Crop & Soil Configuration | AIML FARMER",
    page_icon="🌱",
    layout="wide"
)


# --------------------------------------------------
# PREMIUM DARK GREEN THEME
# --------------------------------------------------

st.markdown("""
<style>

/* MAIN BACKGROUND */

.stApp {
    background-color: #0B1711;
    color: #E8F5EA;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1250px;
}


/* HEADINGS AND TEXT */

h1, h2, h3, h4, p, label {
    color: #E8F5EA !important;
}

.stMarkdown {
    color: #D1E7D6;
}


/* SIDEBAR */

[data-testid="stSidebar"] {
    background-color: #0E1F16;
    border-right: 1px solid #315C3D;
}


/* SELECTBOX */

div[data-baseweb="select"] > div {
    background-color: #142D20 !important;
    border: 1px solid #315C3D !important;
    border-radius: 10px !important;
    color: #E8F5EA !important;
}

div[data-baseweb="select"] span {
    color: #E8F5EA !important;
}

div[data-baseweb="popover"] {
    background-color: #142D20 !important;
}

div[data-baseweb="menu"] {
    background-color: #142D20 !important;
}

div[data-baseweb="menu"] li {
    color: #E8F5EA !important;
}

div[data-baseweb="menu"] li:hover {
    background-color: #245C39 !important;
}


/* NUMBER INPUT */

div[data-testid="stNumberInput"] input {
    background-color: #142D20 !important;
    color: #E8F5EA !important;
    border: 1px solid #315C3D !important;
    border-radius: 10px !important;
}

div[data-testid="stNumberInput"] button {
    background-color: #1C3D29 !important;
    color: #86EFAC !important;
    border: 1px solid #315C3D !important;
}


/* DATE INPUT */

div[data-testid="stDateInput"] input {
    background-color: #142D20 !important;
    color: #E8F5EA !important;
    border: 1px solid #315C3D !important;
    border-radius: 10px !important;
}


/* INPUT FOCUS */

input:focus {
    border-color: #86EFAC !important;
    box-shadow: 0 0 0 1px #86EFAC !important;
}


/* LABELS */

div[data-testid="stWidgetLabel"] p {
    color: #D1E7D6 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}


/* BUTTONS */

.stButton > button {
    background: linear-gradient(120deg, #15803D, #16A34A) !important;
    color: white !important;
    border: 1px solid #347A4B !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    font-weight: 700 !important;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(120deg, #166534, #15803D) !important;
    border-color: #86EFAC !important;
    transform: translateY(-2px);
}


/* DATAFRAME */

div[data-testid="stDataFrame"] {
    border: 1px solid #315C3D;
    border-radius: 12px;
    overflow: hidden;
}


/* SUCCESS AND ERROR */

div[data-testid="stAlert"] {
    border-radius: 12px;
}


/* DIVIDER */

hr {
    border-color: #315C3D !important;
}


/* SCROLLBAR */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #0B1711;
}

::-webkit-scrollbar-thumb {
    background: #315C3D;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown("""
<div style="
background:linear-gradient(120deg,#0E2A1A,#14532D,#166534);
border:1px solid #347A4B;
border-radius:18px;
padding:30px;
margin-bottom:25px;
box-shadow:0 8px 25px rgba(0,0,0,0.2);
">

<div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:2px;">
AIML FARMER / AGRICULTURAL SETTINGS
</div>

<div style="color:#F2FFF5;font-size:30px;font-weight:800;margin-top:10px;">
🌱 Crop & Soil Intelligence
</div>

<div style="color:#D1E7D6;font-size:14px;margin-top:8px;">
Configure crop growth stages and soil properties for smarter irrigation planning.
</div>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# CROP DETAILS
# --------------------------------------------------

st.markdown("""
<div style="
background:#142D20;
border:1px solid #315C3D;
border-radius:13px;
padding:17px 20px;
margin:15px 0;
">

<div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1.5px;">
CROP PROFILE
</div>

<div style="color:#E8F5EA;font-size:21px;font-weight:800;margin-top:6px;">
🌾 Crop Details
</div>

<div style="color:#B8CDBE;font-size:13px;margin-top:5px;">
Define the crop, growth stage, sowing date and cultivated area.
</div>

</div>
""", unsafe_allow_html=True)


st.markdown("""
<div style="
background:#12251B;
border:1px solid #315C3D;
border-radius:15px;
padding:20px;
margin:12px 0 20px 0;
">

<div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1.2px;">
CROP INFORMATION
</div>

<div style="color:#E8F5EA;font-size:17px;font-weight:800;margin-top:6px;">
🌿 Crop & Cultivation Profile
</div>

<div style="color:#B8CDBE;font-size:12px;margin-top:5px;">
Select the crop and provide its cultivation details.
</div>

</div>
""", unsafe_allow_html=True)


col1, col2 = st.columns(2)

with col1:

    crop = st.selectbox(
        "Select Crop",
        ["Wheat", "Rice", "Maize", "Mustard", "Tomato", "Cotton", "Sugarcane"]
    )

    growth_stage = st.selectbox(
        "Growth Stage",
        ["Initial", "Development", "Mid-Season", "Late Season"]
    )

with col2:

    sowing_date = st.date_input("Sowing Date")

    field_area = st.number_input(
        "Field Area (Hectares)",
        min_value=0.01,
        value=1.0
    )


# --------------------------------------------------
# SOIL PROPERTIES
# --------------------------------------------------

st.markdown("""
<div style="
background:#142D20;
border:1px solid #315C3D;
border-radius:13px;
padding:17px 20px;
margin:25px 0 18px 0;
">

<div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1.5px;">
SOIL PROFILE
</div>

<div style="color:#E8F5EA;font-size:21px;font-weight:800;margin-top:6px;">
🪴 Soil Properties
</div>

<div style="color:#B8CDBE;font-size:13px;margin-top:5px;">
Define soil characteristics to support accurate water availability calculations.
</div>

</div>
""", unsafe_allow_html=True)


col3, col4 = st.columns(2)

with col3:

    soil_type = st.selectbox(
        "Soil Type",
        ["Sandy", "Loamy", "Clay", "Silty", "Sandy Loam"]
    )

    field_capacity = st.number_input(
        "Field Capacity (%)",
        min_value=1.0,
        max_value=100.0,
        value=30.0
    )

with col4:

    wilting_point = st.number_input(
        "Permanent Wilting Point (%)",
        min_value=0.0,
        max_value=99.0,
        value=12.0
    )

    root_depth = st.number_input(
        "Root Depth (m)",
        min_value=0.1,
        max_value=3.0,
        value=0.6
    )


# --------------------------------------------------
# SAVE CONFIGURATION
# --------------------------------------------------

st.markdown("""
<div style="
background:#142D20;
border:1px solid #315C3D;
border-radius:13px;
padding:18px 20px;
margin:25px 0 15px 0;
">

<div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1.5px;">
CONFIGURATION MANAGEMENT
</div>

<div style="color:#E8F5EA;font-size:21px;font-weight:800;margin-top:6px;">
💾 Save Crop Configuration
</div>

<div style="color:#B8CDBE;font-size:13px;margin-top:5px;">
Validate and permanently store your crop and soil profile.
</div>

</div>
""", unsafe_allow_html=True)


if st.button(
    "💾 Save Configuration",
    use_container_width=True,
    type="primary"
):

    if field_capacity <= wilting_point:

        st.error("Field Capacity must be greater than Wilting Point.")

    else:

        config = {
            "crop": crop,
            "growth_stage": growth_stage,
            "sowing_date": str(sowing_date),
            "field_area": field_area,
            "soil_type": soil_type,
            "field_capacity": field_capacity,
            "wilting_point": wilting_point,
            "root_depth": root_depth
        }

        save_crop_configuration(config)

        st.success("Configuration saved permanently in database!")


# --------------------------------------------------
# SAVED CONFIGURATIONS
# --------------------------------------------------

st.markdown("""
<div style="
background:#142D20;
border:1px solid #315C3D;
border-radius:15px;
padding:19px 22px;
margin:28px 0 15px 0;
">

<div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1.5px;">
CONFIGURATION ARCHIVE
</div>

<div style="color:#E8F5EA;font-size:23px;font-weight:800;margin-top:7px;">
📋 Saved Crop & Soil Profiles
</div>

<div style="color:#B8CDBE;font-size:13px;margin-top:6px;">
View your previously saved crop and soil configurations.
</div>

</div>
""", unsafe_allow_html=True)


configs = get_crop_configurations()


if configs:

    st.dataframe(
        configs,
        use_container_width=True,
        hide_index=True
    )

else:

    st.markdown("""
<div style="
background:#142D20;
border:1px dashed #477456;
border-radius:15px;
padding:28px;
text-align:center;
margin-top:12px;
">

<div style="font-size:28px;">🌱</div>

<div style="color:#E8F5EA;font-size:18px;font-weight:800;margin-top:9px;">
No Configurations Available
</div>

<div style="color:#B8CDBE;font-size:13px;margin-top:7px;">
Save your first crop and soil profile to build your configuration library.
</div>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div style="
border-top:1px solid #315C3D;
padding:20px 5px;
margin-top:30px;
text-align:center;
">

<div style="color:#86EFAC;font-size:13px;font-weight:800;letter-spacing:1.5px;">
🌱 AIML FARMER
</div>

<div style="color:#B8CDBE;font-size:12px;margin-top:6px;">
Smart Agriculture Intelligence Platform
</div>

<div style="color:#82998A;font-size:11px;margin-top:5px;">
Crop and soil profiles for smarter farm management.
</div>

</div>
""", unsafe_allow_html=True)