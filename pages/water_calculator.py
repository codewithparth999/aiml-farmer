import streamlit as st

from services.database import get_fields, save_report, get_reports


st.set_page_config(
    page_title="Water Calculator | AIML FARMER",
    page_icon="💧",
    layout="wide"
)


# --------------------------------------------------
# MASTER UI THEME
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0B1711;
    color: #E8F5EA;
}

[data-testid="stSidebar"] {
    background-color: #0E1F16;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p, label {
    color: #E8F5EA;
}

.stMarkdown, .stCaption {
    color: #D1E7D6;
}

div[data-testid="stMetric"] {
    background: #142D20;
    border: 1px solid #315C3D;
    padding: 20px;
    border-radius: 14px;
}

div[data-testid="stMetricLabel"] {
    color: #A7D5B3;
}

div[data-testid="stMetricValue"] {
    color: #86EFAC;
}

.stButton > button {
    background: linear-gradient(120deg, #15803D, #16A34A);
    color: white;
    border: 1px solid #347A4B;
    border-radius: 10px;
    font-weight: 700;
    padding: 10px 18px;
}

.stButton > button:hover {
    background: linear-gradient(120deg, #166534, #15803D);
    border: 1px solid #86EFAC;
    color: white;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #12251A;
    border-color: #315C3D;
    border-radius: 14px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #315C3D;
    border-radius: 12px;
    overflow: hidden;
}

hr {
    border-color: #315C3D;
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
">

<div style="
color:#86EFAC;
font-size:11px;
font-weight:800;
letter-spacing:2px;
">
AIML FARMER / WATER MANAGEMENT
</div>

<div style="
color:#F2FFF5;
font-size:30px;
font-weight:800;
margin-top:10px;
">
💧 Water Requirement Calculator
</div>

<div style="
color:#D1E7D6;
font-size:14px;
margin-top:8px;
">
Calculate irrigation water requirements, evaluate efficiency
and manage farm water resources intelligently.
</div>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# FIELD SELECTION
# --------------------------------------------------

st.markdown("""
<div style="color:#86EFAC;font-size:12px;font-weight:800;
letter-spacing:1.5px;margin-bottom:10px;">
FIELD CONFIGURATION
</div>
""", unsafe_allow_html=True)

st.subheader("🌾 Field Selection")

fields = get_fields()

if fields:

    field_options = {
        f'{f["field_name"]} | {f["area"]} ha': f
        for f in fields
    }

    selected_field = st.selectbox(
        "Select Registered Field",
        list(field_options.keys())
    )

    field = field_options[selected_field]
    default_area = float(field["area"])

    st.markdown(f"""
    <div style="
    background:#142D20;
    border:1px solid #315C3D;
    border-radius:14px;
    padding:18px 22px;
    margin:12px 0 20px 0;
    ">

    <div style="
    color:#86EFAC;
    font-size:11px;
    font-weight:800;
    letter-spacing:1.2px;
    ">
    SELECTED FIELD PROFILE
    </div>

    <div style="
    color:#E8F5EA;
    font-size:21px;
    font-weight:800;
    margin-top:8px;
    ">
    {field['field_name']}
    </div>

    <div style="
    color:#B8CDBE;
    font-size:13px;
    margin-top:8px;
    ">
    🌱 Crop: {field['crop']}
    &nbsp; | &nbsp;
    🧪 Soil: {field['soil_type']}
    &nbsp; | &nbsp;
    📐 Area: {field['area']} ha
    </div>

    </div>
    """, unsafe_allow_html=True)

else:

    selected_field = st.text_input("Field Name", "My Field")
    default_area = 2.0

    st.info("No registered fields found. Enter field details manually.")


# --------------------------------------------------
# IRRIGATION PARAMETERS
# --------------------------------------------------

st.divider()

st.markdown("""
<div style="color:#86EFAC;font-size:12px;font-weight:800;
letter-spacing:1.5px;margin-bottom:10px;">
CALCULATION INPUTS
</div>
""", unsafe_allow_html=True)

st.subheader("🧪 Irrigation Parameters")

st.caption(
    "Configure your field area, irrigation depth, system efficiency and rainfall."
)

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown("**🌾 Field & Irrigation Details**")

        area = st.number_input(
            "Field Area (hectares)",
            min_value=0.1,
            max_value=1000.0,
            value=default_area
        )

        net_depth = st.number_input(
            "Net Irrigation Depth (mm)",
            min_value=0.0,
            max_value=500.0,
            value=25.0
        )

with col2:

    with st.container(border=True):

        st.markdown("**💧 Water Efficiency & Rainfall**")

        efficiency = st.slider(
            "Irrigation Efficiency (%)",
            min_value=30,
            max_value=100,
            value=85
        )

        rainfall = st.number_input(
            "Effective Rainfall (mm)",
            min_value=0.0,
            max_value=200.0,
            value=0.0
        )


# --------------------------------------------------
# CALCULATION ENGINE
# --------------------------------------------------

st.markdown("""
<div style="color:#86EFAC;font-size:12px;font-weight:800;
letter-spacing:1.5px;margin-top:15px;margin-bottom:10px;">
WATER ANALYSIS ENGINE
</div>
""", unsafe_allow_html=True)

st.markdown("### ⚙️ Water Calculation Engine")

st.caption(
    "Calculate the estimated irrigation water requirement for your selected field."
)

if st.button(
    "💧 Calculate Water Requirement",
    use_container_width=True,
    type="primary"
):

    if not selected_field.strip():

        st.error("Please enter a valid field name.")

    else:

        effective_depth = max(0, net_depth - rainfall)
        gross_depth = effective_depth / (efficiency / 100)

        water_liters = gross_depth * area * 10000
        water_cubic_meters = water_liters / 1000

        result = {
            "Report Type": "Water Requirement Calculation",
            "Field": selected_field,
            "Area (hectares)": area,
            "Net Irrigation Depth (mm)": net_depth,
            "Effective Rainfall (mm)": rainfall,
            "Efficiency (%)": efficiency,
            "Effective Depth (mm)": round(effective_depth, 2),
            "Gross Irrigation Depth (mm)": round(gross_depth, 2),
            "Water Required (Liters)": round(water_liters),
            "Water Volume (m3)": round(water_cubic_meters, 2)
        }

        st.session_state["water_calculation"] = result


# --------------------------------------------------
# CALCULATION RESULTS
# --------------------------------------------------

if "water_calculation" in st.session_state:

    result = st.session_state["water_calculation"]

    st.divider()

    # RESULT HEADER

    st.markdown("""
    <div style="
    background:linear-gradient(110deg,#142D20,#183B2B);
    border:1px solid #315C3D;
    border-radius:15px;
    padding:22px;
    margin:15px 0;
    ">

    <div style="
    color:#86EFAC;
    font-size:11px;
    font-weight:800;
    letter-spacing:1.5px;
    ">
    CALCULATION OUTPUT
    </div>

    <div style="
    color:#E8F5EA;
    font-size:24px;
    font-weight:800;
    margin-top:8px;
    ">
    💧 Irrigation Water Analysis
    </div>

    <div style="
    color:#B8CDBE;
    font-size:13px;
    margin-top:7px;
    ">
    Your estimated water requirement and irrigation volume.
    </div>

    </div>
    """, unsafe_allow_html=True)

    # RESULT METRIC CARDS

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(f"""
        <div style="
        background:#12251B;
        border:1px solid #347253;
        border-radius:15px;
        padding:20px;
        min-height:115px;
        ">

        <div style="color:#86EFAC;font-size:11px;font-weight:800;">
        NET WATER DEPTH
        </div>

        <div style="
        color:#E8F5EA;
        font-size:25px;
        font-weight:800;
        margin-top:12px;
        ">
        {result["Effective Depth (mm)"]:.2f} mm
        </div>

        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown(f"""
        <div style="
        background:#12251B;
        border:1px solid #347253;
        border-radius:15px;
        padding:20px;
        min-height:115px;
        ">

        <div style="color:#86EFAC;font-size:11px;font-weight:800;">
        GROSS IRRIGATION DEPTH
        </div>

        <div style="
        color:#E8F5EA;
        font-size:25px;
        font-weight:800;
        margin-top:12px;
        ">
        {result["Gross Irrigation Depth (mm)"]:.2f} mm
        </div>

        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown(f"""
        <div style="
        background:#12251B;
        border:1px solid #347253;
        border-radius:15px;
        padding:20px;
        min-height:115px;
        ">

        <div style="color:#86EFAC;font-size:11px;font-weight:800;">
        WATER REQUIRED
        </div>

        <div style="
        color:#E8F5EA;
        font-size:25px;
        font-weight:800;
        margin-top:12px;
        ">
        {result["Water Required (Liters)"]:,.0f} L
        </div>

        </div>
        """, unsafe_allow_html=True)

    # TOTAL WATER VOLUME

    st.markdown(f"""
    <div style="
    background:linear-gradient(110deg,#142D20,#183B2B);
    border:1px solid #477456;
    border-radius:15px;
    padding:22px;
    margin-top:18px;
    ">

    <div style="
    color:#86EFAC;
    font-size:11px;
    font-weight:800;
    letter-spacing:1.2px;
    ">
    TOTAL WATER VOLUME
    </div>

    <div style="
    color:#E8F5EA;
    font-size:30px;
    font-weight:800;
    margin-top:10px;
    ">
    {result["Water Volume (m3)"]:,.2f} m³
    </div>

    </div>
    """, unsafe_allow_html=True)

    # SUCCESS MESSAGE

    st.markdown(f"""
    <div style="
    background:#142D20;
    border:1px solid #347253;
    border-radius:13px;
    padding:19px 22px;
    margin:20px 0;
    ">

    <div style="
    color:#86EFAC;
    font-size:11px;
    font-weight:800;
    letter-spacing:1px;
    ">
    ✓ CALCULATION COMPLETED
    </div>

    <div style="
    color:#E8F5EA;
    font-size:17px;
    font-weight:700;
    margin-top:9px;
    ">
    Estimated water requirement:
    {result["Water Required (Liters)"]:,.0f} liters
    </div>

    <div style="
    color:#B8CDBE;
    font-size:12px;
    margin-top:6px;
    ">
    Your irrigation water estimate is ready.
    </div>

    </div>
    """, unsafe_allow_html=True)

    # SAVE REPORT

    st.markdown("""
    <div style="color:#86EFAC;font-size:12px;font-weight:800;
    letter-spacing:1.5px;margin-top:20px;margin-bottom:8px;">
    REPORT MANAGEMENT
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💾 Save Calculation Report")

    st.caption(
        "Permanently store this water requirement calculation in your database."
    )

    if st.button(
        "💾 Save Calculation to Database",
        use_container_width=True,
        type="primary"
    ):

        save_report(result)

        st.success("Calculation permanently saved!")

    # DISCLAIMER

    st.caption(
        "Prototype estimate. Confirm that rainfall has not already "
        "been deducted from the entered net irrigation depth."
    )


# --------------------------------------------------
# SAVED CALCULATION HISTORY
# --------------------------------------------------

st.divider()

st.markdown("""
<div style="
background:linear-gradient(110deg,#142D20,#183B2B);
border:1px solid #315C3D;
border-radius:15px;
padding:22px;
margin:15px 0;
">

<div style="
color:#86EFAC;
font-size:11px;
font-weight:800;
letter-spacing:1.5px;
">
REPORT ARCHIVE
</div>

<div style="
color:#E8F5EA;
font-size:24px;
font-weight:800;
margin-top:8px;
">
📚 Saved Calculation History
</div>

<div style="
color:#B8CDBE;
font-size:13px;
margin-top:7px;
">
Review your previously saved irrigation water calculations.
</div>

</div>
""", unsafe_allow_html=True)


reports = get_reports()

water_reports = [
    item["report"] for item in reports
    if item["report"].get("Report Type") == "Water Requirement Calculation"
]

if water_reports:

    st.dataframe(
        water_reports,
        use_container_width=True,
        hide_index=True
    )

else:

    st.markdown("""
    <div style="
    background:#142D20;
    border:1px dashed #477456;
    border-radius:15px;
    padding:30px;
    text-align:center;
    margin-top:15px;
    ">

    <div style="font-size:32px;">📂</div>

    <div style="
    color:#E8F5EA;
    font-size:19px;
    font-weight:800;
    margin-top:10px;
    ">
    No Saved Calculations
    </div>

    <div style="
    color:#B8CDBE;
    font-size:13px;
    margin-top:8px;
    ">
    Your saved water requirement reports will appear here.
    </div>

    </div>
    """, unsafe_allow_html=True)