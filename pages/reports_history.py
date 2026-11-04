import streamlit as st
import pandas as pd
from datetime import datetime

from api_client import get_request, post_request


st.set_page_config(
    page_title="Reports & History | AIML FARMER",
    page_icon="📑",
    layout="wide"
)


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown("""
<div style="
    background:linear-gradient(120deg,#0E2A1A,#14532D,#166534);
    border:1px solid #347A4B;
    border-radius:18px;
    padding:30px;
    margin-bottom:22px;
">
    <div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:2px;">
        AIML FARMER / REPORT MANAGEMENT
    </div>
    <div style="color:#F2FFF5;font-size:30px;font-weight:800;margin-top:10px;">
        📑 Farm Intelligence Report Center
    </div>
    <div style="color:#D1E7D6;font-size:14px;margin-top:8px;">
        Access, review and download your saved irrigation advisories and farm analysis reports.
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SAVE LATEST AI ADVISORY
# --------------------------------------------------

st.markdown("""
<div style="
    background:#142D20;
    border:1px solid #315C3D;
    border-radius:15px;
    padding:19px 22px;
    margin:15px 0;
">
    <div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1.5px;">
        ADVISORY ARCHIVE
    </div>
    <div style="color:#E8F5EA;font-size:22px;font-weight:800;margin-top:7px;">
        💾 Save Latest AI Advisory
    </div>
    <div style="color:#B8CDBE;font-size:13px;margin-top:6px;">
        Store your latest irrigation recommendation permanently in the report database.
    </div>
</div>
""", unsafe_allow_html=True)


if st.button(
    "📥 Save Latest Advisory",
    use_container_width=True,
    type="primary"
):

    result = st.session_state.get("ai_advisory_result")

    if result:

        report = {
            "Date & Time": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "Decision": result["decision"],
            "Crop Water Requirement (mm/day)": result["etc_mm_day"],
            "Soil Water Depletion (mm)": result["adjusted_depletion_mm"],
            "Available Water (mm)": result["total_available_water_mm"],
            "Net Irrigation (mm)": result["net_irrigation_mm"],
            "Gross Irrigation (mm)": result["gross_irrigation_mm"],
            "Water Required (Liters)": result["water_required_liters"]
        }

        response = post_request(
            "/reports",
            {"report": report}
        )

        if response and response.get("status") != "error":
            st.success("Report permanently saved in database!")
        else:
            st.error(
                response.get("message", "Unable to save report.")
                if response else "Backend connection failed."
            )

    else:
        st.warning("Generate an AI Advisory first.")


# --------------------------------------------------
# REPORT HISTORY HEADER
# --------------------------------------------------

st.divider()

st.markdown("""
<div style="
    background:#142D20;
    border:1px solid #315C3D;
    border-radius:15px;
    padding:19px 22px;
    margin:15px 0;
">
    <div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1.5px;">
        REPORT ARCHIVE
    </div>
    <div style="color:#E8F5EA;font-size:23px;font-weight:800;margin-top:7px;">
        📊 Advisory History
    </div>
    <div style="color:#B8CDBE;font-size:13px;margin-top:6px;">
        Review your previously saved irrigation advisories and farm reports.
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# FETCH SAVED REPORTS FROM BACKEND
# --------------------------------------------------

response = get_request("/reports")

if response and response.get("status") != "error":

    saved_reports = response.get("reports", [])

    if saved_reports:

        history = []

        for item in saved_reports:

            report = item.get("report", {}).copy()

            report["Database ID"] = item.get("id")
            report["Saved At"] = item.get("created_at")

            history.append(report)

        df = pd.DataFrame(history)

        # TOTAL REPORTS CARD

        st.markdown(f"""
        <div style="
            background:#142D20;
            border:1px solid #347A4B;
            border-radius:15px;
            padding:20px;
            margin:12px 0 18px 0;
        ">
            <div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1px;">
                TOTAL SAVED REPORTS
            </div>
            <div style="color:#E8F5EA;font-size:32px;font-weight:800;margin-top:9px;">
                {len(df)}
            </div>
            <div style="color:#B8CDBE;font-size:12px;margin-top:5px;">
                Reports stored in your farm database
            </div>
        </div>
        """, unsafe_allow_html=True)

        # REPORT TABLE

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # CSV DOWNLOAD SECTION

        st.markdown("""
        <div style="
            background:#142D20;
            border:1px solid #315C3D;
            border-radius:12px;
            padding:16px 20px;
            margin:18px 0 12px 0;
        ">
            <div style="color:#86EFAC;font-size:11px;font-weight:800;letter-spacing:1px;">
                DATA EXPORT
            </div>
            <div style="color:#E8F5EA;font-size:19px;font-weight:800;margin-top:7px;">
                ⬇️ Download Farm Reports
            </div>
            <div style="color:#B8CDBE;font-size:13px;margin-top:6px;">
                Export your saved report history into a CSV file for further analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Reports (CSV)",
            data=csv,
            file_name="aiml_farmer_reports.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:

        # EMPTY HISTORY STATE

        st.markdown("""
        <div style="
            background:#142D20;
            border:1px dashed #477456;
            border-radius:15px;
            padding:25px;
            text-align:center;
            margin-top:12px;
        ">
            <div style="font-size:28px;">📂</div>
            <div style="color:#E8F5EA;font-size:18px;font-weight:800;margin-top:9px;">
                No Reports Available
            </div>
            <div style="color:#B8CDBE;font-size:13px;margin-top:7px;">
                Generate an AI Advisory and save it to see your reports here.
            </div>
        </div>
        """, unsafe_allow_html=True)

else:

    st.error(
        response.get("message", "Unable to fetch reports from backend.")
        if response else "Backend connection failed. Please start the FastAPI server."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div style="
    border-top:1px solid #315C3D;
    padding:18px 5px;
    margin-top:25px;
    text-align:center;
">
    <div style="color:#86EFAC;font-size:13px;font-weight:800;letter-spacing:1.5px;">
        🌱 AIML FARMER
    </div>
    <div style="color:#B8CDBE;font-size:12px;margin-top:6px;">
        Smart Agriculture Intelligence Platform
    </div>
    <div style="color:#82998A;font-size:11px;margin-top:5px;">
        Your farm reports, securely organized in the SQLite database.
    </div>
</div>
""", unsafe_allow_html=True)
