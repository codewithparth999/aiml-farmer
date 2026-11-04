import streamlit as st
from datetime import datetime

from api_client import get_request, post_request

st.set_page_config(
    page_title="Soil Moisture Monitoring | AIML FARMER",
    page_icon="🌱",
    layout="wide"
)

# --------------------------------------------------
# PREMIUM STYLING
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #08130F;
    color: #E8F1EA;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0D1C16;
    border-right: 1px solid #20372A;
}

h1, h2, h3 {
    color: #E8F5EA !important;
}

p, label {
    color: #B8CDBE;
}

div[data-testid="stMetric"] {
    background: #12251B;
    border: 1px solid #294636;
    border-radius: 14px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    color: #9DB8A5;
}

div[data-testid="stMetricValue"] {
    color: #E7F8EB;
}

div.stButton > button {
    background: linear-gradient(100deg, #35A85D, #21864B);
    color: white;
    border: none;
    border-radius: 11px;
    min-height: 45px;
    font-weight: 700;
}

div.stButton > button:hover {
    background: #43BD6D;
    color: white;
    border: none;
}

hr {
    border-color: #294234;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("🌱 Soil Moisture Intelligence")

st.caption(
    "Monitor soil moisture conditions and make informed irrigation decisions."
)

st.divider()


# --------------------------------------------------
# FETCH REGISTERED FIELDS FROM BACKEND
# --------------------------------------------------

field_response = get_request("/fields")

if field_response.get("status") == "error":
    st.error("Unable to fetch registered fields from backend.")
    st.stop()

fields = field_response.get("fields", [])

field_name = "My Field"
field_id = None

st.subheader("🌾 Field Selection")

if fields:

    field_names = {
        f'{field["field_name"]} | {field["area"]} ha | ID: {field["id"]}': field
        for field in fields
    }

    selected = st.selectbox(
        "Select Registered Field",
        list(field_names.keys())
    )

    field = field_names[selected]

    field_name = field["field_name"]
    field_id = field["id"]

    st.markdown(f"""
    <div style="
        background:#142D20;
        border:1px solid #315C3D;
        border-radius:12px;
        padding:16px 20px;
        margin:12px 0 20px 0;
    ">
        <div style="color:#91C9A0;font-size:11px;font-weight:700;">
            SELECTED FIELD PROFILE
        </div>
        <div style="color:#E8F5EA;font-size:19px;font-weight:750;margin-top:7px;">
            {field['field_name']}
        </div>
        <div style="color:#B8CDBE;font-size:13px;margin-top:7px;">
            🌱 Crop: {field.get('crop', 'N/A')}
            &nbsp; | &nbsp;
            🧪 Soil: {field.get('soil_type', 'N/A')}
            &nbsp; | &nbsp;
            📐 Area: {field.get('area', 0)} ha
        </div>
    </div>
    """, unsafe_allow_html=True)

else:

    st.info("No registered fields found. Enter field details manually.")

    field_name = st.text_input(
        "Field Name",
        value="My Field"
    )


# --------------------------------------------------
# SOIL INPUTS
# --------------------------------------------------

st.divider()

st.subheader("🧪 Soil Parameters")

st.caption(
    "Enter the latest soil moisture and soil water retention values."
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("**🌱 Moisture Reading**")

    moisture = st.number_input(
        "Current Soil Moisture (%)",
        min_value=0.0,
        max_value=100.0,
        value=22.0,
        step=0.5
    )

with col2:

    st.markdown("**💧 Water Retention**")

    field_capacity = st.number_input(
        "Field Capacity (%)",
        min_value=1.0,
        max_value=100.0,
        value=30.0,
        step=0.5
    )

wilting_point = st.number_input(
    "Wilting Point (%)",
    min_value=0.0,
    max_value=99.0,
    value=12.0,
    step=0.5
)


# --------------------------------------------------
# ANALYZE SOIL MOISTURE
# --------------------------------------------------

st.divider()

st.subheader("🔍 Soil Moisture Analysis")

if st.button(
    "ANALYZE SOIL MOISTURE",
    use_container_width=True
):

    if not field_name.strip():

        st.error("Please enter a valid field name.")

    elif field_capacity <= wilting_point:

        st.error(
            "Field Capacity must be greater than Wilting Point."
        )

    elif not wilting_point <= moisture <= field_capacity:

        st.error(
            f"Current moisture must be between "
            f"{wilting_point}% and {field_capacity}%."
        )

    else:

        if moisture < wilting_point + 0.25 * (
            field_capacity - wilting_point
        ):

            status = "Very Low"
            recommendation = (
                "Soil moisture is low. Check irrigation requirement."
            )

        elif moisture < wilting_point + 0.50 * (
            field_capacity - wilting_point
        ):

            status = "Low"
            recommendation = "Monitor soil moisture closely."

        elif moisture < wilting_point + 0.80 * (
            field_capacity - wilting_point
        ):

            status = "Moderate"
            recommendation = (
                "Soil moisture is in a moderate range."
            )

        else:

            status = "High"
            recommendation = (
                "Soil moisture is relatively high."
            )

        st.session_state["soil_analysis"] = {
            "Date & Time": datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            ),
            "Field": field_name,
            "Moisture (%)": moisture,
            "Field Capacity (%)": field_capacity,
            "Wilting Point (%)": wilting_point,
            "Status": status,
            "Recommendation": recommendation,
            "field_id": field_id
        }


# --------------------------------------------------
# ANALYSIS RESULTS
# --------------------------------------------------

if "soil_analysis" in st.session_state:

    result = st.session_state["soil_analysis"]

    st.divider()

    st.subheader("📊 Soil Moisture Intelligence")

    st.caption(
        "Analysis of current soil moisture conditions."
    )

    status_styles = {
        "Very Low": (
            "#3B1F1F", "#FF8585", "🚨", "CRITICAL MOISTURE"
        ),
        "Low": (
            "#392B18", "#FFC66D", "⚠️", "LOW MOISTURE"
        ),
        "Moderate": (
            "#18352C", "#83D9A2", "🌱", "MODERATE MOISTURE"
        ),
        "High": (
            "#173747", "#83D5F0", "💧", "HIGH MOISTURE"
        )
    }

    bg, accent, icon, label = status_styles[result["Status"]]

    st.markdown(f"""
    <div style="
        background:{bg};
        border:1px solid {accent};
        border-radius:16px;
        padding:22px;
        margin:15px 0;
    ">
        <div style="color:{accent};font-size:11px;font-weight:800;
                    letter-spacing:1.5px;">
            SOIL HEALTH STATUS
        </div>
        <div style="font-size:27px;font-weight:800;color:#F3FFF5;
                    margin-top:8px;">
            {icon} {result["Status"]}
        </div>
        <div style="color:#D0DED3;font-size:13px;margin-top:8px;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Current Moisture",
            f'{result["Moisture (%)"]}%'
        )

    with c2:
        st.metric(
            "Field Capacity",
            f'{result["Field Capacity (%)"]}%'
        )

    st.markdown("**Moisture Level Indicator**")

    st.progress(result["Moisture (%)"] / 100)

    st.info(
        f'💡 Recommendation: {result["Recommendation"]}'
    )


    # --------------------------------------------------
    # SAVE SOIL MOISTURE AND REPORT
    # --------------------------------------------------

    st.divider()

    st.subheader("💾 Save Soil Moisture Report")

    st.caption(
        "Store this reading and analysis in the backend database."
    )

    if st.button(
        "SAVE MOISTURE REPORT",
        use_container_width=True
    ):

        moisture_data = {
            "field_id": result["field_id"],
            "moisture": result["Moisture (%)"],
            "source": "Manual Entry",
            "notes": result["Recommendation"]
        }

        # Save moisture reading
        moisture_response = post_request(
            "/soil-moisture",
            moisture_data
        )

        if moisture_response.get("status") == "error":

            st.error(
                f"Moisture reading save failed: "
                f"{moisture_response.get('message')}"
            )

        else:

            # Save analysis report
            report_data = {
                "Report Type": "Soil Moisture Reading",
                **{
                    key: value
                    for key, value in result.items()
                    if key != "field_id"
                }
            }

            report_response = post_request(
                "/reports",
                report_data
            )

            st.success("Soil moisture reading saved successfully!")

            if report_response.get("status") == "error":

                st.warning(
                    "Moisture reading saved, but report could not be saved: "
                    + report_response.get("message", "")
                )

            else:

                st.success("Soil moisture report saved successfully!")

            st.toast("Data saved to backend database!")


# --------------------------------------------------
# SOIL MOISTURE HISTORY
# --------------------------------------------------

st.divider()

st.subheader("📈 Previous Soil Moisture Readings")

history_response = get_request("/soil-moisture")

if history_response.get("status") == "error":

    st.error("Unable to load moisture history.")

else:

    readings = history_response.get("readings", [])

    if readings:

        st.dataframe(
            readings,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Total readings available: {len(readings)}"
        )

    else:

        st.info("No previous soil moisture readings found.")


st.caption(
    "Analysis is based on manually entered readings. "
    "Live IoT sensor integration is not enabled."
)