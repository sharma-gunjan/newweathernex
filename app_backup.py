import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib
import folium
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path
from streamlit_folium import st_folium
from datetime import datetime


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="WeatherNex",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background:
        radial-gradient(
            circle at 20% 10%,
            rgba(29, 78, 121, 0.30),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 30%,
            rgba(13, 148, 136, 0.18),
            transparent 30%
        ),
        #06111f;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #071525;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 2rem 1.1rem;
    }

    /* ---------- TEXT ---------- */

    h1, h2, h3, h4 {
        color: #f8fafc !important;
        letter-spacing: -0.02em;
    }

    p, label, span {
        color: #d7e3f2;
    }

    /* ---------- HERO ---------- */

    .hero {
        background:
        linear-gradient(
            135deg,
            rgba(23, 66, 112, 0.95),
            rgba(9, 116, 139, 0.90)
        );

        border: 1px solid rgba(125,211,252,0.28);
        border-radius: 28px;

        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;

        box-shadow:
        0 20px 50px rgba(0,0,0,0.25);
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #d9f2ff;
    }

    .hero-location {
        margin-top: 1rem;
        font-size: 1rem;
        color: #bce7ff;
    }

    /* ---------- SECTION ---------- */

    .section-title {
        font-size: 1.55rem;
        font-weight: 750;
        margin-top: 1.7rem;
        margin-bottom: 0.8rem;
    }

    .section-subtitle {
        color: #91a7bd;
        margin-bottom: 1.3rem;
    }

    /* ---------- CARDS ---------- */

    .info-card {
        background: rgba(18, 38, 60, 0.90);
        border: 1px solid rgba(125, 211, 252, 0.16);
        border-radius: 20px;
        padding: 1.2rem 1.3rem;
        min-height: 125px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.16);
    }

    .card-label {
        color: #93c5fd;
        font-size: 0.92rem;
        margin-bottom: 0.5rem;
    }

    .card-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 750;
    }

    .card-small {
        color: #8fc9f5;
        margin-top: 0.35rem;
        font-size: 0.86rem;
    }

    /* ---------- ALERT ---------- */

    .alert-card {
        border-radius: 22px;
        padding: 1.4rem 1.6rem;
        margin: 1rem 0 1.6rem 0;
        background: rgba(55, 25, 48, 0.75);
        border: 1px solid rgba(248,113,113,0.65);
    }

    .alert-title {
        font-size: 1.5rem;
        font-weight: 750;
        color: white;
        margin-bottom: 0.4rem;
    }

    .alert-text {
        color: #dbeafe;
        line-height: 1.6;
    }

    /* ---------- RAIN TIMING ---------- */

    .rain-card {
        background:
        linear-gradient(
            135deg,
            rgba(21,65,105,0.95),
            rgba(16,91,117,0.90)
        );

        border: 1px solid rgba(125,211,252,0.25);
        border-radius: 24px;
        padding: 1.6rem;
        margin: 1rem 0;
    }

    .rain-big {
        font-size: 2.15rem;
        font-weight: 800;
        color: white;
    }

    .rain-muted {
        color: #a8d8f5;
        margin-top: 0.3rem;
    }

    /* ---------- COPILOT ---------- */

    .copilot-card {
        background: rgba(20, 38, 60, 0.90);
        border: 1px solid rgba(168,85,247,0.30);
        border-radius: 22px;
        padding: 1.5rem;
    }

    /* ---------- DIVIDER ---------- */

    hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 2rem 0 !important;
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(125,211,252,0.25);
        background: #123b61;
        color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #60a5fa;
        background: #174b78;
    }

    /* ---------- TABS ---------- */

    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #60a5fa !important;
    }

    /* ---------- DATAFRAME ---------- */

    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CITY DATA
# =========================================================

CITIES = {

    "Delhi": {
        "lat": 28.6139,
        "lon": 77.2090
    },

    "Mumbai": {
        "lat": 19.0760,
        "lon": 72.8777
    },

    "Chennai": {
        "lat": 13.0827,
        "lon": 80.2707
    },

    "Kolkata": {
        "lat": 22.5726,
        "lon": 88.3639
    },

    "Bengaluru": {
        "lat": 12.9716,
        "lon": 77.5946
    },

    "Hyderabad": {
        "lat": 17.3850,
        "lon": 78.4867
    },

    "Pune": {
        "lat": 18.5204,
        "lon": 73.8567
    },

    "Ahmedabad": {
        "lat": 23.0225,
        "lon": 72.5714
    }

}


# =========================================================
# WEATHER CODE DESCRIPTION
# =========================================================

WEATHER_CODES = {

    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Depositing rime fog",

    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",

    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",

    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",

    66: "Light freezing rain",
    67: "Heavy freezing rain",

    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",

    77: "Snow grains",

    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",

    85: "Slight snow showers",
    86: "Heavy snow showers",

    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail"
}


# =========================================================
# WEATHER EMOJI
# =========================================================

def weather_emoji(code):

    if code in [0]:
        return "☀️"

    if code in [1, 2]:
        return "🌤️"

    if code in [3]:
        return "☁️"

    if code in [45, 48]:
        return "🌫️"

    if code in [
        51, 53, 55,
        56, 57
    ]:
        return "🌦️"

    if code in [
        61, 63, 65,
        66, 67,
        80, 81, 82
    ]:
        return "🌧️"

    if code in [
        95, 96, 99
    ]:
        return "⛈️"

    return "🌦️"


# =========================================================
# WEATHER API
# =========================================================

@st.cache_data(ttl=600)
def get_weather(lat, lon):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": lat,
        "longitude": lon,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "wind_speed_10m",
            "wind_direction_10m"
        ]),

        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "wind_speed_10m",
            "wind_gusts_10m"
        ]),

        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "precipitation_sum",
            "rain_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "sunrise",
            "sunset"
        ]),

        "forecast_days": 7,
        "timezone": "auto"

    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# HISTORICAL DATA LOADER
# =========================================================

def find_historical_csv():

    base_dir = Path(__file__).resolve().parent

    possible_paths = [

        base_dir / "data" / "weather.csv",

        base_dir / "weather.csv",

        Path("data/weather.csv"),

        Path("weather.csv")

    ]

    for path in possible_paths:

        if path.exists():

            return path

    return None


@st.cache_data
def load_historical_data():

    path = find_historical_csv()

    if path is None:
        return None, None

    try:

        df = pd.read_csv(path)

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        return df, path

    except Exception:

        return None, path


# =========================================================
# MODEL LOADER
# =========================================================

@st.cache_resource
def load_rainfall_model():

    model_path = (
        Path(__file__).resolve().parent
        / "rainfall_model.pkl"
    )

    if not model_path.exists():

        return None

    try:

        return joblib.load(model_path)

    except Exception:

        return None


# =========================================================
# AI PREDICTION
# =========================================================

def predict_rainfall(
    model,
    temperature,
    humidity,
    wind_speed,
    fallback
):

    if model is None:

        return max(
            float(fallback),
            0.0
        )

    try:

        # Most likely model structure
        X = pd.DataFrame({

            "temperature": [
                temperature
            ],

            "humidity": [
                humidity
            ],

            "wind_speed": [
                wind_speed
            ]

        })

        prediction = model.predict(X)

        return max(
            float(prediction[0]),
            0.0
        )

    except Exception:

        try:

            # Try numpy fallback
            X = np.array([
                [
                    temperature,
                    humidity,
                    wind_speed
                ]
            ])

            prediction = model.predict(X)

            return max(
                float(prediction[0]),
                0.0
            )

        except Exception:

            return max(
                float(fallback),
                0.0
            )


# =========================================================
# RISK CALCULATION
# =========================================================

def calculate_risk(
    rain_probability,
    predicted_rainfall,
    wind_speed,
    weather_codes
):

    thunderstorm = any(
        int(code) in [95, 96, 99]
        for code in weather_codes
        if pd.notna(code)
    )

    score = 0

    score += min(
        rain_probability * 0.35,
        35
    )

    score += min(
        predicted_rainfall * 0.55,
        40
    )

    score += min(
        wind_speed * 0.8,
        15
    )

    if thunderstorm:
        score += 10

    score = int(
        max(
            0,
            min(
                100,
                score
            )
        )
    )

    if score >= 80:

        return score, "CRITICAL"

    if score >= 60:

        return score, "HIGH"

    if score >= 35:

        return score, "MODERATE"

    return score, "LOW"


# =========================================================
# RAIN INTENSITY
# =========================================================

def rain_intensity(mm):

    if mm >= 7:
        return "Heavy 🌧️"

    if mm >= 2:
        return "Moderate 🌦️"

    if mm > 0:
        return "Light 🌦️"

    return "No significant rain"


# =========================================================
# RAIN TIMING
# =========================================================

def get_rain_timing(hourly_df):

    if hourly_df.empty:

        return None

    now = pd.Timestamp.now(
        tz=hourly_df["time"].dt.tz
    )

    future = hourly_df[
        hourly_df["time"] >= now
    ].copy()

    if future.empty:

        return None

    # Consider rain when either probability
    # is reasonably high or precipitation exists.

    rain_mask = (
        (future["precipitation_probability"] >= 40)
        |
        (future["precipitation"] > 0)
    )

    rain_hours = future[
        rain_mask
    ].copy()

    if rain_hours.empty:

        return None

    # First expected rain
    first_rain = rain_hours.iloc[0]

    start_time = first_rain["time"]

    # Find continuous rain window
    current_index = first_rain.name

    window = []

    for idx in future.index:

        if idx < current_index:
            continue

        row = future.loc[idx]

        is_rain = (
            row["precipitation_probability"] >= 40
            or row["precipitation"] > 0
        )

        if is_rain:

            window.append(row)

        elif window:

            break

    if not window:

        window = [
            first_rain
        ]

    last_rain = window[-1]

    end_time = last_rain["time"]

    duration_hours = max(
        1,
        len(window)
    )

    max_rain = max(
        float(x["precipitation"])
        for x in window
    )

    max_probability = max(
        float(x["precipitation_probability"])
        for x in window
    )

    return {

        "start": start_time,

        "end": end_time,

        "duration": duration_hours,

        "max_rain": max_rain,

        "probability": max_probability,

        "intensity": rain_intensity(
            max_rain
        )

    }


# =========================================================
# SMART ADVICE
# =========================================================

def generate_advice(
    temperature,
    humidity,
    rain_probability,
    wind_speed,
    predicted_rainfall
):

    advice = []

    if rain_probability >= 70:

        advice.append(
            "☔ Carry an umbrella or raincoat."
        )

    elif rain_probability >= 40:

        advice.append(
            "🌦️ Keep rain protection nearby."
        )

    if predicted_rainfall >= 50:

        advice.append(
            "🚗 Avoid unnecessary travel during peak rainfall."
        )

    if wind_speed >= 35:

        advice.append(
            "💨 Strong winds expected; avoid exposed areas."
        )

    if temperature >= 35:

        advice.append(
            "🥤 Stay hydrated and avoid prolonged sun exposure."
        )

    if humidity >= 80:

        advice.append(
            "💧 High humidity may make conditions feel warmer."
        )

    if not advice:

        advice.append(
            "✅ Weather conditions look relatively manageable."
        )

    return advice


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            padding: 0.5rem 0 1.2rem 0;
        ">
            <div style="
                font-size: 1.45rem;
                font-weight: 800;
                color: white;
            ">
                🌦️ WeatherNex
            </div>

            <div style="
                color:#8fa6bd;
                margin-top:0.35rem;
                font-size:0.88rem;
            ">
                National Weather Intelligence Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    location = st.selectbox(
        "📍 Select Location",
        list(CITIES.keys())
    )

    st.divider()

    if st.button(
        "🔄 Refresh Weather",
        use_container_width=True
    ):

        st.cache_data.clear()

        st.rerun()

    st.divider()

    st.markdown(
        "### 🧠 Intelligence Modules"
    )

    st.markdown(
        """
        🌐 Live Weather

        📈 Historical Analysis

        🤖 AI Rainfall Prediction

        ⚠️ Risk Assessment

        🗺️ Risk Map

        🕐 Hourly Forecast

        📅 7-Day Forecast

        🚨 Smart Early Warning

        🔎 Anomaly Detection

        🎯 Recommended Actions

        🧠 Intelligence Score

        💬 Weather Copilot
        """
    )

    st.divider()

    st.caption(
        "WeatherNex • Weather Intelligence Prototype"
    )


# =========================================================
# FETCH WEATHER
# =========================================================

coords = CITIES[location]

try:

    weather = get_weather(
        coords["lat"],
        coords["lon"]
    )

except Exception as e:

    st.error(
        "Unable to fetch live weather data."
    )

    st.code(
        str(e)
    )

    st.stop()


# =========================================================
# CURRENT DATA
# =========================================================

current = weather["current"]

temperature = float(
    current["temperature_2m"]
)

humidity = float(
    current["relative_humidity_2m"]
)

feels_like = float(
    current["apparent_temperature"]
)

current_precipitation = float(
    current["precipitation"]
)

current_rain = float(
    current["rain"]
)

weather_code = int(
    current["weather_code"]
)

cloud_cover = float(
    current["cloud_cover"]
)

pressure = float(
    current["pressure_msl"]
)

wind_speed = float(
    current["wind_speed_10m"]
)

wind_direction = float(
    current["wind_direction_10m"]
)


# =========================================================
# HOURLY DATAFRAME
# =========================================================

hourly = pd.DataFrame({

    "time": pd.to_datetime(
        weather["hourly"]["time"]
    ),

    "temperature": weather["hourly"][
        "temperature_2m"
    ],

    "humidity": weather["hourly"][
        "relative_humidity_2m"
    ],

    "feels_like": weather["hourly"][
        "apparent_temperature"
    ],

    "rain_probability": weather["hourly"][
        "precipitation_probability"
    ],

    "precipitation": weather["hourly"][
        "precipitation"
    ],

    "rain": weather["hourly"][
        "rain"
    ],

    "weather_code": weather["hourly"][
        "weather_code"
    ],

    "wind_speed": weather["hourly"][
        "wind_speed_10m"
    ],

    "wind_gust": weather["hourly"][
        "wind_gusts_10m"
    ]

})


# =========================================================
# DAILY DATAFRAME
# =========================================================

daily = pd.DataFrame({

    "date": pd.to_datetime(
        weather["daily"]["time"]
    ),

    "weather_code": weather["daily"][
        "weather_code"
    ],

    "max_temp": weather["daily"][
        "temperature_2m_max"
    ],

    "min_temp": weather["daily"][
        "temperature_2m_min"
    ],

    "feels_max": weather["daily"][
        "apparent_temperature_max"
    ],

    "rainfall": weather["daily"][
        "precipitation_sum"
    ],

    "rain": weather["daily"][
        "rain_sum"
    ],

    "rain_probability": weather["daily"][
        "precipitation_probability_max"
    ],

    "max_wind": weather["daily"][
        "wind_speed_10m_max"
    ],

    "sunrise": weather["daily"][
        "sunrise"
    ],

    "sunset": weather["daily"][
        "sunset"
    ]

})


# =========================================================
# NEXT 24 HOURS
# =========================================================

now = pd.Timestamp.now(
    tz=hourly["time"].dt.tz
)

next_24 = hourly[
    hourly["time"] >= now
].head(24).copy()


if next_24.empty:

    next_24 = hourly.head(24).copy()


rain_probability_24 = float(
    next_24["rain_probability"].max()
)

rainfall_24 = float(
    next_24["precipitation"].sum()
)


# =========================================================
# AI RAINFALL PREDICTION
# =========================================================

historical_df, historical_path = (
    load_historical_data()
)

model = load_rainfall_model()

fallback_rainfall = (
    rainfall_24
)

predicted_rainfall = predict_rainfall(

    model,

    temperature,

    humidity,

    wind_speed,

    fallback_rainfall

)


# =========================================================
# HISTORICAL AVERAGE
# =========================================================

historical_avg = 0.0

if historical_df is not None:

    historical_df.columns = (
        historical_df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    if (
        "location" in historical_df.columns
        and
        "rainfall" in historical_df.columns
    ):

        historical_df["location"] = (
            historical_df["location"]
            .astype(str)
            .str.strip()
        )

        historical_df["rainfall"] = pd.to_numeric(
            historical_df["rainfall"],
            errors="coerce"
        )

        city_history = historical_df[
            historical_df["location"].str.lower()
            ==
            location.lower()
        ].copy()

        city_history = city_history.dropna(
            subset=["rainfall"]
        )

        if not city_history.empty:

            historical_avg = float(
                city_history["rainfall"].mean()
            )


# =========================================================
# RISK
# =========================================================

risk_score, risk_level = calculate_risk(

    rain_probability_24,

    predicted_rainfall,

    wind_speed,

    next_24["weather_code"].tolist()

)


# =========================================================
# HERO
# =========================================================

st.markdown(
    f"""
    <div class="hero">

        <div class="hero-title">
            🌦️ WeatherNex
        </div>

        <div class="hero-subtitle">
            National Weather Intelligence Platform
        </div>

        <div class="hero-location">
            📍 {location}
            &nbsp; • &nbsp;
            {WEATHER_CODES.get(weather_code, "Weather")}
            &nbsp; {weather_emoji(weather_code)}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP TABS
# =========================================================

tabs = st.tabs([
    "📊 Overview",
    "🕐 Hourly Forecast",
    "📅 7-Day Forecast",
    "🗺️ Risk Map",
    "📈 Historical Analysis",
    "🚨 Early Warning",
    "💬 Weather Copilot"
])


# =========================================================
# TAB 1 — OVERVIEW
# =========================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">🌤️ Current Weather</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Live weather conditions and real-time intelligence.'
        '</div>',
        unsafe_allow_html=True
    )

    # METRICS
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.markdown(
            f"""
            <div class="info-card">

                <div class="card-label">
                    🌡️ Temperature
                </div>

                <div class="card-value">
                    {temperature:.1f}°C
                </div>

                <div class="card-small">
                    Feels like {feels_like:.1f}°C
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="info-card">

                <div class="card-label">
                    🌧️ Rain Probability
                </div>

                <div class="card-value">
                    {rain_probability_24:.0f}%
                </div>

                <div class="card-small">
                    Next 24 hours
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="info-card">

                <div class="card-label">
                    💧 Humidity
                </div>

                <div class="card-value">
                    {humidity:.0f}%
                </div>

                <div class="card-small">
                    Relative humidity
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            f"""
            <div class="info-card">

                <div class="card-label">
                    💨 Wind Speed
                </div>

                <div class="card-value">
                    {wind_speed:.1f}
                </div>

                <div class="card-small">
                    km/h
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c5:

        st.markdown(
            f"""
            <div class="info-card">

                <div class="card-label">
                    ⚠️ Risk Level
                </div>

                <div class="card-value">
                    {risk_level}
                </div>

                <div class="card-small">
                    Score {risk_score}/100
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # SPACE
    st.markdown("<br>", unsafe_allow_html=True)

    # CURRENT CONDITIONS
    st.markdown(
        """
        <div class="info-card">

            <div style="
                font-size:1.25rem;
                font-weight:700;
                color:white;
            ">
                🌤️ Current Conditions
            </div>

            <div style="
                margin-top:0.8rem;
                color:#c4d9ec;
                line-height:1.8;
            ">
        """,
        unsafe_allow_html=True
    )

    st.write(
        f"{weather_emoji(weather_code)} "
        f"**{WEATHER_CODES.get(weather_code, 'Unknown')}**"
    )

    st.write(
        f"☁️ Cloud cover: **{cloud_cover:.0f}%**"
        f"  •  "
        f"📊 Pressure: **{pressure:.0f} hPa**"
        f"  •  "
        f"🧭 Wind direction: **{wind_direction:.0f}°**"
    )

    st.write(
        f"🌧️ Current precipitation: "
        f"**{current_precipitation:.1f} mm**"
    )

    st.markdown(
        "</div></div>",
        unsafe_allow_html=True
    )

    # RISK ALERT
    st.markdown("<br>", unsafe_allow_html=True)

    if risk_level == "CRITICAL":

        st.markdown(
            f"""
            <div class="alert-card">

                <div class="alert-title">
                    🔴 Critical Weather Risk
                </div>

                <div class="alert-text">
                    Heavy rainfall, strong winds or
                    thunderstorm conditions may create
                    hazardous outdoor conditions.
                    Stay alert and follow local warnings.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    elif risk_level == "HIGH":

        st.markdown(
            f"""
            <div class="alert-card">

                <div class="alert-title">
                    🟠 High Weather Risk
                </div>

                <div class="alert-text">
                    Significant rainfall or strong weather
                    conditions may affect travel and
                    outdoor activities.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    elif risk_level == "MODERATE":

        st.info(
            "🟡 Moderate weather risk. "
            "Keep monitoring upcoming conditions."
        )

    else:

        st.success(
            "🟢 Low weather risk. "
            "No major immediate threat detected."
        )

    # RAIN TIMING
    st.markdown(
        '<div class="section-title">🌧️ Rain Timing Intelligence</div>',
        unsafe_allow_html=True
    )

    rain_info = get_rain_timing(
        next_24
    )

    if rain_info is not None:

        start_text = rain_info[
            "start"
        ].strftime("%I:%M %p")

        end_text = rain_info[
            "end"
        ].strftime("%I:%M %p")

        st.markdown(
            f"""
            <div class="rain-card">

                <div class="rain-big">
                    🌧️ Rain expected
                </div>

                <div class="rain-muted">
                    Forecast estimate based on hourly weather data.
                </div>

                <hr>

                <b>⏰ Expected Start</b><br>
                {start_text}

                <br><br>

                <b>🛑 Expected End</b><br>
                {end_text}

                <br><br>

                <b>⏱️ Estimated Duration</b><br>
                {rain_info["duration"]} hour(s)

                <br><br>

                <b>💧 Expected Intensity</b><br>
                {rain_info["intensity"]}

                <br><br>

                <b>🎯 Peak Rain Probability</b><br>
                {rain_info["probability"]:.0f}%

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.success(
            "☀️ No significant rainfall window "
            "is currently detected in the next 24 hours."
        )

    # ACTIONS
    st.markdown(
        '<div class="section-title">🎯 Recommended Actions</div>',
        unsafe_allow_html=True
    )

    advice = generate_advice(

        temperature,

        humidity,

        rain_probability_24,

        wind_speed,

        predicted_rainfall

    )

    for item in advice:

        st.info(item)


# =========================================================
# TAB 2 — HOURLY FORECAST
# =========================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">🕐 Hourly Forecast</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Next 24 hours of temperature, rain probability and precipitation.'
        '</div>',
        unsafe_allow_html=True
    )

    hourly_view = next_24.copy()

    hourly_view["Time"] = hourly_view[
        "time"
    ].dt.strftime("%I:%M %p")

    hourly_view["Temperature (°C)"] = (
        hourly_view["temperature"].round(1)
    )

    hourly_view["Rain Probability (%)"] = (
        hourly_view["rain_probability"].round(0)
    )

    hourly_view["Rainfall (mm)"] = (
        hourly_view["precipitation"].round(1)
    )

    hourly_view["Wind (km/h)"] = (
        hourly_view["wind_speed"].round(1)
    )

    display_hourly = hourly_view[[
        "Time",
        "Temperature (°C)",
        "Rain Probability (%)",
        "Rainfall (mm)",
        "Wind (km/h)"
    ]]

    st.dataframe(
        display_hourly,
        use_container_width=True,
        hide_index=True
    )

    # TEMPERATURE CHART
    temp_chart = px.line(

        hourly_view,

        x="time",

        y="temperature",

        markers=True,

        title="🌡️ Hourly Temperature"

    )

    temp_chart.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        temp_chart,
        use_container_width=True,
        key="hourly_temperature_chart"
    )

    # RAIN PROBABILITY
    rain_chart = px.bar(

        hourly_view,

        x="time",

        y="rain_probability",

        title="🌧️ Hourly Rain Probability"

    )

    rain_chart.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Probability (%)",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        rain_chart,
        use_container_width=True,
        key="hourly_rain_probability_chart"
    )

    # PRECIPITATION
    precip_chart = px.bar(

        hourly_view,

        x="time",

        y="precipitation",

        title="💧 Expected Hourly Rainfall"

    )

    precip_chart.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Rainfall (mm)",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        precip_chart,
        use_container_width=True,
        key="hourly_precipitation_chart"
    )


# =========================================================
# TAB 3 — 7 DAY FORECAST
# =========================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">📅 7-Day Forecast</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Extended weather outlook for the selected city.'
        '</div>',
        unsafe_allow_html=True
    )

    forecast_display = daily.copy()

    forecast_display["Day"] = (
        forecast_display["date"]
        .dt.strftime("%a, %d %b")
    )

    forecast_display["Condition"] = (
        forecast_display["weather_code"]
        .apply(
            lambda x:
            f"{weather_emoji(int(x))} "
            f"{WEATHER_CODES.get(int(x), 'Unknown')}"
        )
    )

    forecast_display["Min (°C)"] = (
        forecast_display["min_temp"]
        .round(1)
    )

    forecast_display["Max (°C)"] = (
        forecast_display["max_temp"]
        .round(1)
    )

    forecast_display["Rain (mm)"] = (
        forecast_display["rainfall"]
        .round(1)
    )

    forecast_display["Rain Probability (%)"] = (
        forecast_display["rain_probability"]
        .round(0)
    )

    forecast_display["Max Wind (km/h)"] = (
        forecast_display["max_wind"]
        .round(1)
    )

    display_forecast = forecast_display[[
        "Day",
        "Condition",
        "Min (°C)",
        "Max (°C)",
        "Rain (mm)",
        "Rain Probability (%)",
        "Max Wind (km/h)"
    ]]

    st.dataframe(
        display_forecast,
        use_container_width=True,
        hide_index=True
    )

    forecast_chart = px.bar(

        forecast_display,

        x="Day",

        y="rainfall",

        title="🌧️ 7-Day Rainfall Forecast"

    )

    forecast_chart.update_layout(
        height=420,
        xaxis_title="Day",
        yaxis_title="Rainfall (mm)",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        forecast_chart,
        use_container_width=True,
        key="seven_day_rainfall_chart"
    )

    temp_forecast_chart = go.Figure()

    temp_forecast_chart.add_trace(
        go.Scatter(

            x=daily["date"],

            y=daily["max_temp"],

            mode="lines+markers",

            name="Maximum Temperature"

        )
    )

    temp_forecast_chart.add_trace(
        go.Scatter(

            x=daily["date"],

            y=daily["min_temp"],

            mode="lines+markers",

            name="Minimum Temperature"

        )
    )

    temp_forecast_chart.update_layout(

        title="🌡️ 7-Day Temperature Forecast",

        height=420,

        xaxis_title="Day",

        yaxis_title="Temperature (°C)"

    )

    st.plotly_chart(
        temp_forecast_chart,
        use_container_width=True,
        key="seven_day_temperature_chart"
    )


# =========================================================
# TAB 4 — RISK MAP
# =========================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">🗺️ Regional Weather Risk Map</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Weather risk intelligence across major Indian cities.'
        '</div>',
        unsafe_allow_html=True
    )

    map_data = []

    for city_name, city_info in CITIES.items():

        try:

            city_weather = get_weather(
                city_info["lat"],
                city_info["lon"]
            )

            city_hourly = pd.DataFrame({

                "rain_probability":
                    city_weather["hourly"][
                        "precipitation_probability"
                    ],

                "precipitation":
                    city_weather["hourly"][
                        "precipitation"
                    ],

                "wind":
                    city_weather["hourly"][
                        "wind_speed_10m"
                    ],

                "weather_code":
                    city_weather["hourly"][
                        "weather_code"
                    ]

            })

            city_rain_probability = float(
                city_hourly[
                    "rain_probability"
                ].head(24).max()
            )

            city_predicted_rain = float(
                city_hourly[
                    "precipitation"
                ].head(24).sum()
            )

            city_wind = float(
                city_hourly[
                    "wind"
                ].head(24).max()
            )

            city_score, city_risk = calculate_risk(

                city_rain_probability,

                city_predicted_rain,

                city_wind,

                city_hourly[
                    "weather_code"
                ].head(24).tolist()

            )

            map_data.append({

                "city": city_name,

                "lat": city_info["lat"],

                "lon": city_info["lon"],

                "risk": city_risk,

                "score": city_score,

                "rain_probability":
                    city_rain_probability,

                "rainfall":
                    city_predicted_rain

            })

        except Exception:

            continue

    map_df = pd.DataFrame(
        map_data
    )

    # MAP
    weather_map = folium.Map(

        location=[
            21.5,
            78.9
        ],

        zoom_start=5,

        tiles="CartoDB dark_matter"

    )

    risk_colors = {

        "LOW": "green",

        "MODERATE": "orange",

        "HIGH": "red",

        "CRITICAL": "darkred"

    }

    for _, row in map_df.iterrows():

        popup_html = f"""
        <div style="
            font-family:Arial;
            width:220px;
        ">

            <h4>
                🌦️ {row['city']}
            </h4>

            <b>Risk:</b>
            {row['risk']}
            <br><br>

            <b>Risk Score:</b>
            {row['score']}/100
            <br>

            <b>Rain Probability:</b>
            {row['rain_probability']:.0f}%
            <br>

            <b>Next 24h Rainfall:</b>
            {row['rainfall']:.1f} mm

        </div>
        """

        folium.CircleMarker(

            location=[
                row["lat"],
                row["lon"]
            ],

            radius=10,

            color=risk_colors.get(
                row["risk"],
                "blue"
            ),

            fill=True,

            fill_color=risk_colors.get(
                row["risk"],
                "blue"
            ),

            fill_opacity=0.8,

            popup=folium.Popup(
                popup_html,
                max_width=300
            )

        ).add_to(weather_map)

    st_folium(
        weather_map,
        width=None,
        height=600,
        key="weather_risk_map"
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.dataframe(
        map_df[
            [
                "city",
                "risk",
                "score",
                "rain_probability",
                "rainfall"
            ]
        ].rename(
            columns={
                "city": "City",
                "risk": "Risk",
                "score": "Score",
                "rain_probability":
                    "Rain Probability (%)",
                "rainfall":
                    "Next 24h Rainfall (mm)"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 5 — HISTORICAL ANALYSIS
# =========================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">📈 Historical Rainfall Analysis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Historical data compared with AI rainfall prediction.'
        '</div>',
        unsafe_allow_html=True
    )

    if historical_df is None:

        st.error(
            "❌ Historical dataset could not be found."
        )

        st.info(
            "Expected location: "
            "`data/weather.csv`"
        )

        st.write(
            "Your GitHub structure should be:"
        )

        st.code(
            """
newweathernex/
│
├── app.py
├── requirements.txt
├── rainfall_model.pkl
│
└── data/
    └── weather.csv
            """
        )

    else:

        st.success(
            f"✅ Historical dataset loaded"
        )

        if historical_path is not None:

            st.caption(
                f"Loaded from: {historical_path}"
            )

        if (
            "location" in historical_df.columns
            and
            "rainfall" in historical_df.columns
        ):

            city_history = historical_df[
                historical_df["location"]
                .astype(str)
                .str.lower()
                ==
                location.lower()
            ].copy()

            city_history["rainfall"] = pd.to_numeric(
                city_history["rainfall"],
                errors="coerce"
            )

            city_history = city_history.dropna(
                subset=["rainfall"]
            )

            if not city_history.empty:

                h1, h2, h3 = st.columns(3)

                with h1:

                    st.metric(
                        "🌧️ AI Predicted Rainfall",
                        f"{predicted_rainfall:.1f} mm"
                    )

                with h2:

                    st.metric(
                        "📊 Historical Average",
                        f"{historical_avg:.1f} mm"
                    )

                with h3:

                    if historical_avg > 0:

                        deviation = (

                            (
                                predicted_rainfall
                                - historical_avg
                            )
                            /
                            historical_avg

                        ) * 100

                        st.metric(
                            "📈 Deviation",
                            f"{deviation:.1f}%"
                        )

                    else:

                        st.metric(
                            "📈 Deviation",
                            "N/A"
                        )

                # Historical chart

                if "date" in city_history.columns:

                    city_history["date"] = pd.to_datetime(
                        city_history["date"],
                        errors="coerce"
                    )

                    city_history = city_history.dropna(
                        subset=["date"]
                    )

                    historical_chart = px.line(

                        city_history.sort_values("date"),

                        x="date",

                        y="rainfall",

                        markers=True,

                        title=f"📈 Historical Rainfall — {location}"

                    )

                    historical_chart.update_layout(
                        height=420,
                        xaxis_title="Date",
                        yaxis_title="Rainfall (mm)"
                    )

                    st.plotly_chart(

                        historical_chart,

                        use_container_width=True,

                        key="historical_rainfall_chart"

                    )

                # Dataset preview

                st.markdown(
                    "### 📋 Historical Dataset"
                )

                st.dataframe(
                    city_history,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    f"No historical records found for {location}."
                )

        else:

            st.error(
                "CSV must contain at least "
                "`location` and `rainfall` columns."
            )


# =========================================================
# TAB 6 — EARLY WARNING
# =========================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">🚨 Smart Early Warning System</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Automatically detects potentially dangerous weather conditions.'
        '</div>',
        unsafe_allow_html=True
    )

    max_rainfall = float(
        daily["rainfall"].max()
    )

    max_rain_date = daily.loc[
        daily["rainfall"].idxmax(),
        "date"
    ]

    max_probability = float(
        daily["rain_probability"].max()
    )

    max_wind = float(
        daily["max_wind"].max()
    )

    e1, e2, e3, e4 = st.columns(4)

    with e1:

        st.metric(
            "🌧️ Max Rainfall",
            f"{max_rainfall:.1f} mm"
        )

    with e2:

        st.metric(
            "☔ Max Rain Probability",
            f"{max_probability:.0f}%"
        )

    with e3:

        st.metric(
            "💨 Max Wind",
            f"{max_wind:.1f} km/h"
        )

    with e4:

        st.metric(
            "⚠️ Risk Score",
            f"{risk_score}/100"
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    if max_rainfall >= 80:

        st.error(
            f"""
            🚨 CRITICAL WARNING

            Very heavy rainfall may occur around
            {max_rain_date.strftime('%d %b %Y')}.

            Potential impacts include waterlogging,
            flooding and travel disruption.
            """
        )

    elif max_rainfall >= 50:

        st.warning(
            f"""
            ⚠️ HIGH WARNING

            Heavy rainfall may occur around
            {max_rain_date.strftime('%d %b %Y')}.

            Stay alert and monitor local weather updates.
            """
        )

    elif max_rainfall >= 25:

        st.info(
            f"""
            🟡 MODERATE WARNING

            Moderate rainfall may occur around
            {max_rain_date.strftime('%d %b %Y')}.
            """
        )

    else:

        st.success(
            "🟢 No major rainfall warning detected."
        )

    # ANOMALY
    st.markdown(
        '<div class="section-title">🔎 Weather Anomaly Detection</div>',
        unsafe_allow_html=True
    )

    if historical_avg > 0:

        anomaly_ratio = (
            predicted_rainfall
            /
            historical_avg
        )

        if anomaly_ratio >= 2:

            st.error(
                "🚨 Significant rainfall anomaly detected. "
                "Predicted rainfall is more than twice "
                "the historical average."
            )

        elif anomaly_ratio >= 1.5:

            st.warning(
                "⚠️ Moderate rainfall anomaly detected. "
                "Predicted rainfall is significantly above "
                "the historical average."
            )

        else:

            st.success(
                "✅ Rainfall is within the expected "
                "historical range."
            )

    else:

        st.info(
            "Historical average unavailable, "
            "so anomaly comparison cannot be calculated."
        )


# =========================================================
# INTELLIGENCE SCORE
# =========================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">🧠 Weather Intelligence Score</div>',
        unsafe_allow_html=True
    )

    st.progress(
        risk_score / 100
    )

    if risk_score >= 80:

        score_text = "Critical weather conditions"

    elif risk_score >= 60:

        score_text = "High weather concern"

    elif risk_score >= 35:

        score_text = "Moderate weather concern"

    else:

        score_text = "Low weather concern"

    st.write(
        f"### {risk_score}/100 — {score_text}"
    )

    st.caption(
        "Score combines rainfall probability, "
        "expected rainfall, wind conditions and "
        "thunderstorm signals."
    )


# =========================================================
# TAB 7 — WEATHER COPILOT
# =========================================================

with tabs[6]:

    st.markdown(
        '<div class="section-title">💬 Weather Copilot</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Ask questions about the current weather, rain timing, '
        'forecast and safety recommendations.'
        '</div>',
        unsafe_allow_html=True
    )

    if "copilot_messages" not in st.session_state:

        st.session_state.copilot_messages = []

    # Previous messages

    for message in st.session_state.copilot_messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    question = st.chat_input(
        "Ask Weather Copilot..."
    )

    if question:

        st.session_state.copilot_messages.append({

            "role": "user",

            "content": question

        })

        q = question.lower().strip()

        rain_info = get_rain_timing(
            next_24
        )

        # -----------------------------
        # DYNAMIC ANSWERS
        # -----------------------------

        if (
            "rain" in q
            and
            (
                "when" in q
                or
                "start" in q
                or
                "kab" in q
            )
        ):

            if rain_info:

                answer = (

                    f"🌧️ {location} mein rain ka "
                    f"forecasted start approximately "
                    f"**{rain_info['start'].strftime('%I:%M %p')}** "
                    f"hai. "
                    f"Expected end approximately "
                    f"**{rain_info['end'].strftime('%I:%M %p')}** "
                    f"hai, with an estimated duration of "
                    f"**{rain_info['duration']} hour(s)**."
                )

            else:

                answer = (
                    "☀️ Next 24 hours mein significant "
                    "rain window detect nahi hui."
                )

        elif (
            "duration" in q
            or
            "kitni der" in q
            or
            "khtm" in q
            or
            "end" in q
        ):

            if rain_info:

                answer = (

                    f"⏱️ Current forecast ke according "
                    f"rain approximately "
                    f"**{rain_info['duration']} hour(s)** "
                    f"tak continue ho sakti hai, "
                    f"around "
                    f"**{rain_info['end'].strftime('%I:%M %p')}** "
                    f"tak."
                )

            else:

                answer = (
                    "🌤️ Significant rainfall window "
                    "currently detected nahi hai."
                )

        elif (
            "umbrella" in q
            or
            "chhatri" in q
            or
            "carry" in q
        ):

            if rain_probability_24 >= 60:

                answer = (
                    f"☔ Yes. {location} mein next 24 hours "
                    f"rain probability **{rain_probability_24:.0f}%** "
                    f"hai, so umbrella carry karna better rahega."
                )

            else:

                answer = (
                    f"🌤️ Rain probability around "
                    f"**{rain_probability_24:.0f}%** hai. "
                    f"Umbrella optional hai, but keeping one "
                    f"nearby won't hurt."
                )

        elif (
            "temperature" in q
            or
            "temp" in q
            or
            "degree" in q
            or
            "garmi" in q
        ):

            answer = (

                f"🌡️ Current temperature in {location} is "
                f"**{temperature:.1f}°C**, while it feels like "
                f"**{feels_like:.1f}°C**."
            )

        elif (
            "humidity" in q
            or
            "humid" in q
        ):

            answer = (

                f"💧 Current humidity is "
                f"**{humidity:.0f}%**. "
                f"High humidity can make the temperature "
                f"feel warmer than the actual temperature."
            )

        elif (
            "wind" in q
            or
            "hawa" in q
        ):

            answer = (

                f"💨 Wind speed in {location} is "
                f"**{wind_speed:.1f} km/h**, "
                f"with a direction of approximately "
                f"**{wind_direction:.0f}°**."
            )

        elif (
            "forecast" in q
            or
            "tomorrow" in q
            or
            "kal" in q
        ):

            tomorrow = daily.iloc[1]

            answer = (

                f"📅 Tomorrow's forecast for {location}: "
                f"{weather_emoji(int(tomorrow['weather_code']))} "
                f"**{WEATHER_CODES.get(int(tomorrow['weather_code']), 'Unknown')}**, "
                f"temperature "
                f"**{tomorrow['min_temp']:.1f}–"
                f"{tomorrow['max_temp']:.1f}°C**, "
                f"rain probability "
                f"**{tomorrow['rain_probability']:.0f}%**, "
                f"expected rainfall "
                f"**{tomorrow['rainfall']:.1f} mm**."
            )

        elif (
            "safe" in q
            or
            "travel" in q
            or
            "outdoor" in q
            or
            "bahar" in q
        ):

            if risk_level in [
                "HIGH",
                "CRITICAL"
            ]:

                answer = (

                    f"⚠️ Outdoor plans ke liye "
                    f"**caution recommended**. "
                    f"Current risk level is **{risk_level}** "
                    f"with a score of **{risk_score}/100**. "
                    f"Heavy rain or strong weather conditions "
                    f"may affect travel."
                )

            else:

                answer = (

                    f"✅ Current risk level is "
                    f"**{risk_level}** "
                    f"with a score of **{risk_score}/100**. "
                    f"Normal precautions ke saath outdoor plans "
                    f"generally manageable hain."
                )

        elif (
            "risk" in q
            or
            "danger" in q
            or
            "alert" in q
        ):

            answer = (

                f"⚠️ Current weather risk in {location} is "
                f"**{risk_level} ({risk_score}/100)**. "
                f"Next 24 hours mein maximum rain probability "
                f"**{rain_probability_24:.0f}%** hai."
            )

        else:

            answer = (

                f"🌦️ Here's the current weather picture for "
                f"**{location}**:\n\n"

                f"🌡️ Temperature: **{temperature:.1f}°C**\n\n"

                f"💧 Humidity: **{humidity:.0f}%**\n\n"

                f"🌧️ Rain probability: "
                f"**{rain_probability_24:.0f}%**\n\n"

                f"💨 Wind: **{wind_speed:.1f} km/h**\n\n"

                f"⚠️ Risk: **{risk_level} "
                f"({risk_score}/100)**\n\n"

                f"You can ask me things like "
                f"**'rain kab start hogi?'**, "
                f"**'umbrella le jaun?'**, "
                f"**'kal ka weather kya hai?'** "
                f"or **'travel safe hai?'**"
            )

        st.session_state.copilot_messages.append({

            "role": "assistant",

            "content": answer

        })

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#71869d;
        padding:1rem;
    ">
        🌦️ <b>WeatherNex</b>
        &nbsp; • &nbsp;
        Weather Intelligence Platform
        &nbsp; • &nbsp;
        Live data powered by Open-Meteo
    </div>
    """,
    unsafe_allow_html=True
)
