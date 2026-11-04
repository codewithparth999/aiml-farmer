import streamlit as st
import pandas as pd

from api_client import get_request, post_request


st.set_page_config(
    page_title="Irrigation Decision Lab | AIML FARMER",
    page_icon="🧪",
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
AIML FARMER / IRRIGATION INTELLIGENCE
</div>

<div style="
color:#F2FFF5;
font-size:30px;
font-weight:800;
margin-top:10px;
">
🧪 Irrigation Decision Lab
</div>

<div style="
color:#D1E7D6;
font-size:14px;
margin-top:8px;
">
Compare multiple irrigation scenarios, evaluate water consumption
and explore smarter field-level decisions.
</div>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# FIELD CONFIGURATION - BACKEND CONNECTED
# --------------------------------------------------

st.markdown("""
<div style="color:#86EFAC;font-size:12px;font-weight:800;
letter-spacing:1.5px;margin-bottom:10px;">
FIELD CONFIGURATION
</div>
""", unsafe_allow_html=True)

st.subheader("🌾 Configure Your Field")

st.caption(
    "Select a registered farm field to begin your irrigation analysis."
)

fields_response = get_request("/fields")

if fields_response.get("status") == "error":

    st.error(
        f"Unable to load fields: {fields_response.get('message')}"
    )
    st.stop()

fields = fields_response.get("fields", [])

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
    🌱 Crop: {field.get('crop') or 'N/A'}
    &nbsp; | &nbsp;
    🧪 Soil: {field.get('soil_type') or 'N/A'}
    &nbsp; | &nbsp;
    📐 Area: {field['area']} ha
    </div>

    </div>
    """, unsafe_allow_html=True)

else:

    selected_field = st.text_input("Field Name", "My Field")
    default_area = 2.0

    st.info(
        "No registered fields found. Enter field details manually."
    )


# --------------------------------------------------
# IRRIGATION PARAMETERS
# --------------------------------------------------

st.divider()

st.markdown("""
<div style="color:#86EFAC;font-size:12px;font-weight:800;
letter-spacing:1.5px;margin-bottom:10px;">
IRRIGATION INPUTS
</div>
""", unsafe_allow_html=True)

st.subheader("🧪 Irrigation Parameters")

st.caption(
    "Configure field area, irrigation depth, expected rainfall and system efficiency."
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
            max_value=200.0,
            value=25.0
        )

with col2:

    with st.container(border=True):

        st.markdown("**💧 Rainfall & Water Efficiency**")

        rainfall = st.number_input(
            "Expected Effective Rainfall (mm)",
            min_value=0.0,
            max_value=200.0,
            value=0.0
        )

        efficiency = st.slider(
            "Irrigation Efficiency (%)",
            min_value=30,
            max_value=100,
            value=85
        )


# --------------------------------------------------
# SCENARIO COMPARISON
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
SCENARIO ANALYSIS
</div>

<div style="
color:#E8F5EA;
font-size:24px;
font-weight:800;
margin-top:8px;
">
📊 Compare Irrigation Scenarios
</div>

<div style="
color:#B8CDBE;
font-size:13px;
margin-top:7px;
">
Evaluate low, normal and high water requirements
for your selected field.
</div>

</div>
""", unsafe_allow_html=True)


scenarios = {
    "Low Water": 0.75,
    "Normal Water": 1.0,
    "High Water": 1.25
}

results = []

for name, factor in scenarios.items():

    adjusted_depth = max(0, net_depth * factor - rainfall)

    gross_depth = adjusted_depth / (efficiency / 100)

    water_liters = gross_depth * area * 10000

    results.append({
        "Scenario": name,
        "Net Depth (mm)": round(adjusted_depth, 2),
        "Gross Depth (mm)": round(gross_depth, 2),
        "Water Required (Liters)": round(water_liters)
    })


df = pd.DataFrame(results)


# --------------------------------------------------
# SCENARIO RESULTS TABLE
# --------------------------------------------------

st.markdown("### 📋 Scenario-wise Water Requirements")

st.caption(
    "Detailed comparison of irrigation depth and total water consumption."
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Scenario": st.column_config.TextColumn(
            "Irrigation Scenario"
        ),
        "Net Depth (mm)": st.column_config.NumberColumn(
            "Net Depth",
            format="%.2f mm"
        ),
        "Gross Depth (mm)": st.column_config.NumberColumn(
            "Gross Depth",
            format="%.2f mm"
        ),
        "Water Required (Liters)": st.column_config.NumberColumn(
            "Water Required",
            format="%,.0f L"
        )
    }
)


# --------------------------------------------------
# WATER USAGE COMPARISON CHART
# --------------------------------------------------

st.markdown("""
<div style="
background:linear-gradient(110deg,#142D20,#183B2B);
border:1px solid #315C3D;
border-radius:15px;
padding:22px;
margin:20px 0 12px 0;
">

<div style="
color:#86EFAC;
font-size:11px;
font-weight:800;
letter-spacing:1.5px;
">
WATER CONSUMPTION ANALYTICS
</div>

<div style="
color:#E8F5EA;
font-size:23px;
font-weight:800;
margin-top:8px;
">
📈 Water Usage Comparison
</div>

<div style="
color:#B8CDBE;
font-size:13px;
margin-top:7px;
">
Visual comparison of water requirements across all three scenarios.
</div>

</div>
""", unsafe_allow_html=True)


st.bar_chart(
    df.set_index("Scenario")["Water Required (Liters)"]
)


# --------------------------------------------------
# CUSTOM SCENARIO SIMULATOR
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
CUSTOM SCENARIO SIMULATOR
</div>

<div style="
color:#E8F5EA;
font-size:23px;
font-weight:800;
margin-top:8px;
">
⚙️ Try Your Own Irrigation Scenario
</div>

<div style="
color:#B8CDBE;
font-size:13px;
margin-top:7px;
">
Adjust irrigation depth and instantly explore its
estimated water requirement.
</div>

</div>
""", unsafe_allow_html=True)


custom_depth = st.slider(
    "Custom Net Irrigation Depth (mm)",
    0.0,
    100.0,
    25.0
)


custom_effective = max(0, custom_depth - rainfall)

custom_gross = custom_effective / (efficiency / 100)

custom_liters = custom_gross * area * 10000


# --------------------------------------------------
# CUSTOM SCENARIO RESULTS
# --------------------------------------------------

st.markdown("### 📌 Custom Scenario Results")

c1, c2 = st.columns(2)

with c1:

    st.markdown(f"""
    <div style="
    background:#12251B;
    border:1px solid #347253;
    border-radius:15px;
    padding:22px;
    min-height:125px;
    ">

    <div style="
    color:#86EFAC;
    font-size:11px;
    font-weight:800;
    ">
    GROSS IRRIGATION DEPTH
    </div>

    <div style="
    color:#E8F5EA;
    font-size:27px;
    font-weight:800;
    margin-top:12px;
    ">
    {custom_gross:.2f} mm
    </div>

    <div style="
    color:#B8CDBE;
    font-size:12px;
    margin-top:7px;
    ">
    Required gross water depth
    </div>

    </div>
    """, unsafe_allow_html=True)

with c2:

    st.markdown(f"""
    <div style="
    background:#12251B;
    border:1px solid #347253;
    border-radius:15px;
    padding:22px;
    min-height:125px;
    ">

    <div style="
    color:#86EFAC;
    font-size:11px;
    font-weight:800;
    ">
    ESTIMATED WATER VOLUME
    </div>

    <div style="
    color:#E8F5EA;
    font-size:27px;
    font-weight:800;
    margin-top:12px;
    ">
    {custom_liters:,.0f} L
    </div>

    <div style="
    color:#B8CDBE;
    font-size:12px;
    margin-top:7px;
    ">
    Water required for selected field
    </div>

    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# SAVE DECISION REPORT - BACKEND CONNECTED
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
REPORT MANAGEMENT
</div>

<div style="
color:#E8F5EA;
font-size:23px;
font-weight:800;
margin-top:8px;
">
💾 Save Decision Lab Report
</div>

<div style="
color:#B8CDBE;
font-size:13px;
margin-top:7px;
">
Store your scenario comparison and custom irrigation results
in the database.
</div>

</div>
""", unsafe_allow_html=True)


if st.button(
    "💾 Save Decision Lab Results",
    use_container_width=True,
    type="primary"
):

    report = {
        "Report Type": "Irrigation Decision Lab",
        "Field": selected_field,
        "Area (ha)": area,
        "Expected Rainfall (mm)": rainfall,
        "Efficiency (%)": efficiency,
        "Scenarios": results,
        "Custom Net Depth (mm)": custom_depth,
        "Custom Gross Depth (mm)": round(custom_gross, 2),
        "Custom Water Volume (Liters)": round(custom_liters)
    }

    report_response = post_request("/reports", report)

    if report_response.get("status") == "error":

        st.error(
            f"Report could not be saved: {report_response.get('message')}"
        )

    else:

        st.success(
            "Decision Lab results saved permanently!"
        )


# --------------------------------------------------
# DISCLAIMER
# --------------------------------------------------

st.markdown("""
<div style="
background:#292516;
border:1px solid #75602D;
border-radius:12px;
padding:18px 21px;
margin-top:22px;
">

<div style="
color:#E8C66D;
font-size:11px;
font-weight:800;
letter-spacing:1px;
">
⚠️ IMPORTANT DISCLAIMER
</div>

<div style="
color:#F3E8C7;
font-size:13px;
line-height:1.7;
margin-top:8px;
">
These are hypothetical comparison scenarios, not validated
irrigation recommendations. Use actual field measurements
and local agricultural guidance before making irrigation decisions.
</div>

</div>
""", unsafe_allow_html=True)
