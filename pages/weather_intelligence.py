import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="Weather Intelligence | AIML FARMER",
    page_icon="🌦️",
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
# BACKEND CONFIGURATION
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000"

LOCATIONS = {
    "Rohtak, Haryana": (28.8955, 76.6066),
    "Ambala, Haryana": (30.3782, 76.7767),
    "Kurukshetra, Haryana": (29.9695, 76.8783)
}

WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snowfall ❄️",
    73: "Moderate snowfall ❄️",
    75: "Heavy snowfall ❄️",
    80: "Rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Heavy rain showers 🌧️",
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with hail ⛈️",
    99: "Severe thunderstorm ⛈️"
}


# --------------------------------------------------
# WEATHER API - CONNECTED TO FASTAPI BACKEND
# --------------------------------------------------

@st.cache_data(ttl=900)
def get_weather(latitude, longitude):

    response = requests.get(
        f"{API_URL}/weather",
        params={
            "latitude": latitude,
            "longitude": longitude
        },
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero-box">
    <div class="hero-tag">SMART AGRICULTURE INTELLIGENCE PLATFORM</div>
    <div class="hero-title">🌦️ Weather Intelligence</div>
    <div class="hero-subtitle">
        Live weather monitoring, forecast analysis and
        agricultural weather insights for smarter farm decisions.
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOCATION SELECTION
# --------------------------------------------------

st.markdown(
    '<div class="section-label">LOCATION MONITORING</div>',
    unsafe_allow_html=True
)

st.subheader("📍 Field Weather Overview")

location_col, info_col = st.columns([2, 1])

with location_col:
    city = st.selectbox(
        "📍 Select Farm Location",
        list(LOCATIONS.keys())
    )

with info_col:
    st.markdown("### 🌍 Weather Source")
    st.success("FastAPI + Open-Meteo API")

latitude, longitude = LOCATIONS[city]

if st.button("🔄 Refresh Weather", use_container_width=True):
    get_weather.clear()


# --------------------------------------------------
# FETCH WEATHER DATA
# --------------------------------------------------

try:

    with st.spinner("Fetching live weather data..."):

        data = get_weather(latitude, longitude)

    current = data["current"]
    daily = data["daily"]

    st.success(f"Live weather data loaded for {city}")

    st.caption(
        f"Coordinates: {latitude}, {longitude} | "
        f"Last updated: {current.get('time', 'Not available')} | "
        f"Source: FastAPI + Open-Meteo"
    )

    # --------------------------------------------------
    # CURRENT WEATHER
    # --------------------------------------------------

    st.divider()

    st.markdown(
        '<div class="section-label">LIVE WEATHER CONDITIONS</div>',
        unsafe_allow_html=True
    )

    st.subheader("🌤️ Current Weather")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🌡️ Temperature",
        f"{current['temperature_2m']} °C"
    )

    col2.metric(
        "💧 Humidity",
        f"{current['relative_humidity_2m']}%"
    )

    col3.metric(
        "🌧️ Precipitation",
        f"{current['precipitation']} mm"
    )

    col4.metric(
        "💨 Wind Speed",
        f"{current['wind_speed_10m']} km/h"
    )

    weather_code = current.get("weather_code", 0)

    st.info(
        f"**Current Condition:** "
        f"{WEATHER_CODES.get(weather_code, 'Weather condition unavailable')}"
        f"\n\n**Feels Like:** "
        f"{current.get('apparent_temperature', 'N/A')} °C"
    )

    # --------------------------------------------------
    # AGRICULTURAL INSIGHTS
    # --------------------------------------------------

    st.divider()

    st.markdown(
        '<div class="section-label">AI-ASSISTED FARM INSIGHTS</div>',
        unsafe_allow_html=True
    )

    st.subheader("🌱 Agricultural Weather Insights")

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    rainfall = current["precipitation"]
    wind = current["wind_speed_10m"]

    insights = []

    if temperature >= 35:
        insights.append((
            "🌡️ High Temperature",
            "Monitor crop water demand and check soil moisture."
        ))

    elif temperature <= 10:
        insights.append((
            "🌡️ Low Temperature",
            "Monitor crops for possible cold-weather stress."
        ))

    else:
        insights.append((
            "🌡️ Temperature",
            "Continue monitoring temperature and crop conditions."
        ))

    if humidity >= 80:
        insights.append((
            "💧 High Humidity",
            "Check crops regularly for conditions favorable to fungal diseases."
        ))

    elif humidity <= 35:
        insights.append((
            "💧 Low Humidity",
            "Check soil moisture because dry air can increase water loss."
        ))

    else:
        insights.append((
            "💧 Humidity",
            "Humidity can influence crop evapotranspiration."
        ))

    if rainfall > 0:
        insights.append((
            "🌧️ Rainfall",
            "Consider measured rainfall before planning irrigation."
        ))

    else:
        insights.append((
            "🌧️ Rainfall",
            "No precipitation is recorded for the current weather interval."
        ))

    if wind >= 25:
        insights.append((
            "💨 Strong Wind",
            "Consider wind conditions when planning irrigation."
        ))

    else:
        insights.append((
            "💨 Wind",
            "Monitor wind speed because it can influence water loss."
        ))

    for title, description in insights:

        with st.container(border=True):

            st.markdown(f"### {title}")

            st.write(description)

    # --------------------------------------------------
    # FIVE DAY FORECAST
    # --------------------------------------------------

    st.divider()

    st.markdown(
        '<div class="section-label">UPCOMING WEATHER CONDITIONS</div>',
        unsafe_allow_html=True
    )

    st.subheader("📅 5-Day Weather Outlook")

    forecast_columns = st.columns(5)

    for index, col in enumerate(forecast_columns):

        with col:

            with st.container(border=True):

                code = daily["weather_code"][index]

                date = daily["time"][index]

                formatted_date = datetime.strptime(
                    date,
                    "%Y-%m-%d"
                ).strftime("%d %b")

                st.markdown(f"### 📅 {formatted_date}")

                st.write(
                    WEATHER_CODES.get(
                        code,
                        "Condition unavailable"
                    )
                )

                st.metric(
                    "⬆️ Max Temperature",
                    f"{daily['temperature_2m_max'][index]} °C"
                )

                st.metric(
                    "⬇️ Min Temperature",
                    f"{daily['temperature_2m_min'][index]} °C"
                )

                st.divider()

                st.write(
                    f"🌧️ **Rainfall:** "
                    f"{daily['precipitation_sum'][index]} mm"
                )

                probability = daily[
                    "precipitation_probability_max"
                ][index]

                if probability is not None:

                    st.write(
                        f"☔ **Rain Probability:** {probability}%"
                    )

                else:

                    st.write(
                        "☔ **Rain Probability:** N/A"
                    )

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    st.divider()

    st.caption(
        "Weather information is retrieved through the AIML FARMER "
        "backend using Open-Meteo forecast models. Forecasts are estimates "
        "and may differ from actual field conditions."
    )


# --------------------------------------------------
# ERROR HANDLING
# --------------------------------------------------

except requests.exceptions.ConnectionError:

    st.error(
        "Backend connection failed. Please make sure FastAPI "
        "is running on http://127.0.0.1:8000."
    )

except requests.exceptions.Timeout:

    st.error(
        "Weather request timed out. Please refresh and try again."
    )

except requests.exceptions.HTTPError as e:

    st.error(
        f"Backend returned an HTTP error: {e}"
    )

except requests.exceptions.RequestException as e:

    st.error(
        f"Unable to fetch weather data: {e}"
    )

except (KeyError, IndexError, ValueError, TypeError):

    st.error(
        "Weather data could not be processed. Please refresh and try again."
    )
    