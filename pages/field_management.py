import streamlit as st

from api_client import (
    get_request,
    post_request,
    put_request,
    delete_request
)

st.set_page_config(
    page_title="Field Management | AIML FARMER",
    page_icon="🌾",
    layout="wide"
)


# ---------------- MASTER UI THEME ----------------

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

/* Dataframe */

[data-testid="stDataFrame"] {
    border: 1px solid #315C3D;
    border-radius: 10px;
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


# ---------------- HERO SECTION ----------------

st.markdown("""
<div class="hero-box">
    <div class="hero-tag">SMART AGRICULTURE INTELLIGENCE PLATFORM</div>
    <div class="hero-title">🌾 Field Management</div>
    <div class="hero-subtitle">
        Manage your agricultural fields, monitor registered crops
        and organize your farm information in one place.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- FETCH FIELDS ----------------

def fetch_fields():

    response = get_request("/fields")

    if response.get("status") == "error":
        st.error(f"Backend Error: {response.get('message')}")
        return []

    return response.get("fields", [])


fields = fetch_fields()


# ---------------- FARM OVERVIEW ----------------

total_fields = len(fields)

total_area = sum(
    float(field.get("area") or 0)
    for field in fields
)

total_crops = len(set(
    field.get("crop")
    for field in fields
    if field.get("crop")
))

st.markdown('<div class="section-label">FARM ANALYTICS</div>',
            unsafe_allow_html=True)

st.subheader("📊 Farm Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Fields", total_fields, "Registered fields")
col2.metric("Total Area", f"{total_area:.2f} ha", "Cultivated area")
col3.metric("Crop Types", total_crops, "Different crops")


st.divider()


# ---------------- ADD NEW FIELD ----------------

st.markdown('<div class="section-label">FIELD REGISTRATION</div>',
            unsafe_allow_html=True)

st.subheader("➕ Register New Field")

st.caption(
    "Add your farm details to start monitoring and managing irrigation."
)

st.info(
    "🌱 Register your field once. You can use its details across the agriculture platform."
)

with st.form("field_form"):

    field_name = st.text_input("Field Name")

    col1, col2 = st.columns(2)

    with col1:
        area = st.number_input(
            "Area (Hectares)",
            min_value=0.01,
            value=1.0
        )

        location = st.text_input("Location")

    with col2:
        crop = st.selectbox(
            "Crop",
            ["Wheat", "Rice", "Maize", "Mustard",
             "Tomato", "Cotton", "Other"]
        )

        soil_type = st.selectbox(
            "Soil Type",
            ["Sandy", "Loamy", "Clay", "Silty", "Sandy Loam"]
        )

    irrigation_method = st.selectbox(
        "Irrigation Method",
        ["Drip", "Sprinkler", "Flood", "Furrow", "Other"]
    )

    st.caption(
        "All field details should be accurate for better irrigation recommendations."
    )

    submitted = st.form_submit_button(
        "Save Field",
        use_container_width=True
    )

    if submitted:

        if not field_name.strip():
            st.error("Please enter a field name.")

        else:

            field_data = {
                "field_name": field_name.strip(),
                "area": area,
                "location": location,
                "crop": crop,
                "soil_type": soil_type,
                "irrigation_method": irrigation_method
            }

            response = post_request("/fields", field_data)

            if response.get("status") == "error":
                st.error(response.get("message"))

            else:
                st.success("Field saved successfully!")
                st.rerun()


st.divider()


# ---------------- REGISTERED FIELDS ----------------

st.markdown('<div class="section-label">FIELD DIRECTORY</div>',
            unsafe_allow_html=True)

st.subheader("📁 Registered Fields")

search_query = st.text_input(
    "🔍 Search Fields",
    placeholder="Search by field name or location..."
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:

    crop_options = ["All Crops"] + sorted(set(
        f["crop"] for f in fields if f.get("crop")
    ))

    selected_crop = st.selectbox(
        "Filter by Crop",
        crop_options
    )

with filter_col2:

    soil_options = ["All Soil Types"] + sorted(set(
        f["soil_type"] for f in fields if f.get("soil_type")
    ))

    selected_soil = st.selectbox(
        "Filter by Soil Type",
        soil_options
    )


filtered_fields = fields.copy()

if search_query:

    filtered_fields = [
        f for f in filtered_fields
        if search_query.lower() in str(f.get("field_name", "")).lower()
        or search_query.lower() in str(f.get("location", "")).lower()
    ]


if selected_crop != "All Crops":

    filtered_fields = [
        f for f in filtered_fields
        if f.get("crop") == selected_crop
    ]


if selected_soil != "All Soil Types":

    filtered_fields = [
        f for f in filtered_fields
        if f.get("soil_type") == selected_soil
    ]


# ---------------- FIELD SUMMARY ----------------

if filtered_fields:

    st.subheader("🌱 Field Summary")

    for field in filtered_fields:

        with st.container(border=True):

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:

                st.markdown(
                    f"### 🌾 {field.get('field_name', 'Unnamed Field')}"
                )

                st.caption(
                    f"📍 {field.get('location') or 'Location not specified'}"
                )

            with col2:

                st.metric(
                    "Area",
                    f"{field.get('area', 0)} ha"
                )

            with col3:

                st.markdown(f"**Crop:** {field.get('crop') or 'N/A'}")
                st.markdown(f"**Soil:** {field.get('soil_type') or 'N/A'}")
                st.markdown(
                    f"**Irrigation:** {field.get('irrigation_method') or 'N/A'}"
                )


st.divider()


# ---------------- COMPLETE FIELD RECORDS ----------------

st.subheader("📋 Complete Field Records")

if filtered_fields:

    st.dataframe(
        filtered_fields,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Showing {len(filtered_fields)} of {len(fields)} registered fields."
    )

elif fields:

    st.warning("No fields match your search or selected filters.")

else:

    st.info("No fields registered yet. Add your first farm field above.")


# ---------------- UPDATE FIELD ----------------

st.divider()

st.markdown('<div class="section-label">FIELD CONFIGURATION</div>',
            unsafe_allow_html=True)

st.subheader("✏️ Update Field")

if fields:

    field_options = {
        f"{f.get('field_name', 'Unnamed')} (ID: {f.get('id')})": f
        for f in fields
        if f.get("id") is not None
    }

    if field_options:

        selected_name = st.selectbox(
            "Select Field to Update",
            list(field_options.keys()),
            key="update_field"
        )

        selected_field = field_options[selected_name]

        with st.form("update_field_form"):

            new_name = st.text_input(
                "Field Name",
                value=selected_field.get("field_name", "")
            )

            new_area = st.number_input(
                "Area (Hectares)",
                min_value=0.01,
                value=max(float(selected_field.get("area") or 1), 0.01),
                key="update_area"
            )

            new_location = st.text_input(
                "Location",
                value=selected_field.get("location") or ""
            )

            new_crop = st.selectbox(
                "Crop",
                ["Wheat", "Rice", "Maize", "Mustard",
                 "Tomato", "Cotton", "Other"],
                index=(
                    ["Wheat", "Rice", "Maize", "Mustard",
                     "Tomato", "Cotton", "Other"].index(
                        selected_field.get("crop")
                    )
                    if selected_field.get("crop") in
                    ["Wheat", "Rice", "Maize", "Mustard",
                     "Tomato", "Cotton", "Other"]
                    else 0
                )
            )

            new_soil = st.selectbox(
                "Soil Type",
                ["Sandy", "Loamy", "Clay", "Silty", "Sandy Loam"],
                index=(
                    ["Sandy", "Loamy", "Clay", "Silty", "Sandy Loam"].index(
                        selected_field.get("soil_type")
                    )
                    if selected_field.get("soil_type") in
                    ["Sandy", "Loamy", "Clay", "Silty", "Sandy Loam"]
                    else 0
                )
            )

            new_irrigation = st.selectbox(
                "Irrigation Method",
                ["Drip", "Sprinkler", "Flood", "Furrow", "Other"],
                index=(
                    ["Drip", "Sprinkler", "Flood", "Furrow", "Other"].index(
                        selected_field.get("irrigation_method")
                    )
                    if selected_field.get("irrigation_method") in
                    ["Drip", "Sprinkler", "Flood", "Furrow", "Other"]
                    else 0
                )
            )

            update_submitted = st.form_submit_button(
                "Update Field",
                use_container_width=True
            )

            if update_submitted:

                updated_data = {
                    "field_name": new_name,
                    "area": new_area,
                    "location": new_location,
                    "crop": new_crop,
                    "soil_type": new_soil,
                    "irrigation_method": new_irrigation
                }

                response = put_request(
                    f"/fields/{selected_field['id']}",
                    updated_data
                )

                if response.get("status") == "error":
                    st.error(response.get("message"))

                else:
                    st.success("Field updated successfully!")
                    st.rerun()

    else:
        st.info("Field IDs are not available for updating.")

else:
    st.info("Add a field first to enable editing.")


# ---------------- DELETE FIELD ----------------

st.divider()

st.markdown('<div class="section-label">FIELD MANAGEMENT</div>',
            unsafe_allow_html=True)

st.subheader("🗑️ Delete Field")

if fields:

    deletable_fields = {
        f"{f.get('field_name', 'Unnamed')} (ID: {f.get('id')})": f
        for f in fields
        if f.get("id") is not None
    }

    if deletable_fields:

        delete_name = st.selectbox(
            "Select Field to Delete",
            list(deletable_fields.keys()),
            key="delete_field"
        )

        if st.button("Delete Selected Field", type="primary"):

            selected = deletable_fields[delete_name]

            response = delete_request(
                f"/fields/{selected['id']}"
            )

            if response.get("status") == "error":
                st.error(response.get("message"))

            else:
                st.success("Field deleted successfully!")
                st.rerun()

    else:
        st.info("Field IDs are not available for deletion.")

else:
    st.info("No fields available to delete.")