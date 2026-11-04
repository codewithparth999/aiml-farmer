import streamlit as st
import pandas as pd

from api_client import get_request, post_request


st.set_page_config(
    page_title="24-Hour Prediction | AIML FARMER",
    page_icon="📈",
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
AIML FARMER / PREDICTION CENTER
</div>

<div style="
color:#F2FFF5;
font-size:30px;
font-weight:800;
margin-top:10px;
">
24-Hour Soil Moisture Forecast
</div>

<div style="
color:#D1E7D6;
font-size:14px;
margin-top:8px;
">
Explore future soil moisture trends and plan irrigation
with intelligent forecasting insights.
</div>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD REGISTERED FIELDS FROM BACKEND
# --------------------------------------------------

st.markdown("""
<div style="color:#86EFAC;font-size:12px;font-weight:800;
letter-spacing:1.5px;margin-bottom:10px;">
FIELD CONFIGURATION
</div>
""", unsafe_allow_html=True)

st.subheader("🌾 Field Selection")

field_response = get_request("/fields")

fields = []

if field_response and field_response.get("status") != "error":
    fields = field_response.get("fields", [])

field_id = None

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

    field_id = field["id"]

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
    {field["field_name"]}
    </div>

    <div style="
    color:#B8CDBE;
    font-size:13px;
    margin-top:8px;
    ">
    🌱 Crop: {field.get("crop", "N/A")}
    &nbsp; | &nbsp;
    🧪 Soil: {field.get("soil_type", "N/A")}
    &nbsp; | &nbsp;
    📐 Area: {field.get("area", 0)} ha
    </div>

    </div>
    """, unsafe_allow_html=True)

else:

    st.warning("No registered fields found. Enter a field name manually.")

    selected_field = st.text_input("Field Name", "My Field")


# --------------------------------------------------
# PREDICTION PARAMETERS
# --------------------------------------------------

st.divider()

st.markdown("""
<div style="color:#86EFAC;font-size:12px;font-weight:800;
letter-spacing:1.5px;margin-bottom:10px;">
FORECAST CONTROLS
</div>
""", unsafe_allow_html=True)

st.subheader("🧪 Prediction Parameters")

col1, col2 = st.columns(2)

with col1:

    with st.container(border=True):

        st.markdown("**🌱 Current Soil Condition**")

        current = st.number_input(
            "Current Soil Moisture (%)",
            min_value=0.0,
            max_value=100.0,
            value=22.0,
            step=0.5
        )

with col2:

    with st.container(border=True):

        st.markdown("**📉 Expected Moisture Trend**")

        expected_change = st.slider(
            "Expected Moisture Change (%)",
            min_value=-10.0,
            max_value=10.0,
            value=-2.0,
            step=0.5
        )

        if expected_change < 0:
            st.caption("↘ Expected moisture decrease")
        elif expected_change > 0:
            st.caption("↗ Expected moisture increase")
        else:
            st.caption("→ No expected moisture change")


# --------------------------------------------------
# GENERATE FORECAST THROUGH FASTAPI
# --------------------------------------------------

st.divider()

if st.button(
    "📈 Generate 24-Hour Forecast",
    use_container_width=True
):

    if not selected_field.strip():
        st.error("Please enter a valid field name.")

    else:

        payload = {
            "current_moisture": current,
            "expected_change": expected_change
        }

        with st.spinner("Generating forecast through FastAPI..."):

            response = post_request(
                "/hour-prediction",
                payload
            )

        if not response or response.get("status") == "error":

            st.error(
                response.get("message", "Forecast generation failed.")
                if response else "Backend connection failed."
            )

        else:

            forecast = response.get("forecast", [])

            if forecast:

                st.session_state["forecast_data"] = pd.DataFrame(forecast)
                st.session_state["forecast_field"] = selected_field
                st.session_state["forecast_field_id"] = field_id
                st.session_state["forecast_expected_change"] = expected_change

                st.session_state["forecast_source"] = "FastAPI Backend"

                st.success("24-hour forecast generated successfully!")

            else:
                st.error("Backend returned an empty forecast.")


# --------------------------------------------------
# FORECAST RESULTS
# --------------------------------------------------

if "forecast_data" in st.session_state:

    df = st.session_state["forecast_data"]

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
    PREDICTION OUTPUT
    </div>

    <div style="
    color:#E8F5EA;
    font-size:24px;
    font-weight:800;
    margin-top:8px;
    ">
    📈 Soil Moisture Forecast
    </div>

    <div style="
    color:#B8CDBE;
    font-size:13px;
    margin-top:7px;
    ">
    Estimated moisture trend over the next 24 hours.
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.caption("Generated through: FastAPI Backend")

    # CHART

    st.markdown("### 📊 Moisture Trend Analysis")

    st.line_chart(
        df.set_index("Hours Ahead")["Soil Moisture (%)"]
    )

    # METRICS

    st.markdown("### 📌 Forecast Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Moisture",
            f'{df.iloc[0]["Soil Moisture (%)"]:.2f}%'
        )

    with col2:
        st.metric(
            "After 24 Hours",
            f'{df.iloc[-1]["Soil Moisture (%)"]:.2f}%'
        )

    # TABLE

    st.markdown("### 📋 Hour-wise Prediction Details")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Hours Ahead": st.column_config.NumberColumn(
                "Hours Ahead",
                format="%d hrs"
            ),
            "Soil Moisture (%)": st.column_config.NumberColumn(
                "Soil Moisture",
                format="%.2f %%"
            )
        }
    )

    # SAVE REPORT THROUGH BACKEND

    st.divider()

    st.markdown("""
    <div style="color:#86EFAC;font-size:12px;font-weight:800;
    letter-spacing:1.5px;margin-bottom:10px;">
    REPORT MANAGEMENT
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💾 Save Forecast Report")

    if st.button(
        "💾 Save Forecast to Database",
        use_container_width=True,
        type="primary"
    ):

        report = {
            "Report Type": "24-Hour Soil Moisture Forecast",
            "Field": st.session_state["forecast_field"],
            "Current Moisture (%)": float(
                df.iloc[0]["Soil Moisture (%)"]
            ),
            "Expected Change (%)": st.session_state[
                "forecast_expected_change"
            ],
            "Estimated Moisture After 24 Hours (%)": float(
                df.iloc[-1]["Soil Moisture (%)"]
            ),
            "Forecast Data": df.to_dict(orient="records")
        }

        response = post_request(
            "/reports",
            {"report": report}
        )

        if response and response.get("status") != "error":
            st.success("Forecast permanently saved in backend database!")
            st.toast("Forecast report saved successfully!")
        else:
            st.error(
                response.get("message", "Unable to save forecast.")
                if response else "Backend connection failed."
            )

    # DISCLAIMER

    st.markdown("""
    <div style="
    background:#292414;
    border:1px solid #76602C;
    border-radius:12px;
    padding:17px 20px;
    margin-top:20px;
    ">

    <div style="
    color:#E8C878;
    font-weight:800;
    font-size:13px;
    ">
    ⚠️ MODEL VALIDATION NOTICE
    </div>

    <div style="
    color:#D8CCAA;
    font-size:12px;
    margin-top:8px;
    line-height:1.6;
    ">
    This forecast is a formula-based illustrative scenario using the entered
    moisture change. It is not an actual machine-learning prediction.
    </div>

    </div>
    """, unsafe_allow_html=True)


else:

    st.markdown("""
    <div style="
    background:#142D20;
    border:1px dashed #477456;
    border-radius:15px;
    padding:30px;
    text-align:center;
    margin-top:20px;
    ">

    <div style="font-size:34px;">📊</div>

    <div style="
    color:#E8F5EA;
    font-size:20px;
    font-weight:800;
    margin-top:12px;
    ">
    Forecast Awaiting Generation
    </div>

    <div style="
    color:#B8CDBE;
    font-size:13px;
    margin-top:8px;
    ">
    Configure the prediction parameters above and generate
    your 24-hour soil moisture forecast.
    </div>

    </div>
    """, unsafe_allow_html=True)