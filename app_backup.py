import os
from datetime import datetime

import requests
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Optional ML model
try:
    import joblib
except ImportError:
    joblib = None


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="WeatherNex",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #0b1b30 55%, #062d3a 100%);
    }

    [data-testid="stSidebar"] {
        background: #091727;
        border-right: 1px solid #203b57;
    }

    [data-testid="stSidebar"] * {
        color: #e8f1ff;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #f4f8ff !important;
    }

    .hero {
        background: linear-gradient(135deg, #174878, #087c8d);
        padding: 30px 34px;
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.16);
        margin-bottom: 30px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.18);
    }

    .hero h1 {
        font-size: 42px;
        margin: 0;
        color: white !important;
    }

    .hero p {
        color: #dceeff;
        font-size: 17px;
        margin: 8px 0 0;
    }

    .section-title {
        font-size: 26px;
        font-weight: 750;
        color: #f4f8ff;
        margin-top: 28px;
        margin-bottom: 8px;
    }

    .section-subtitle {
        color: #9db3ca;
        font-size: 15px;
        margin-bottom: 20px;
    }

    .info-card {
        background: #10243a;
        border: 1px solid #294663;
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 20px;
    }

    .info-card h3 {
        margin-top: 0;
        font-size: 19px;
    }

    .info-card p {
        color: #c7d8eb;
        line-height: 1.7;
    }

    .metric-card {
        background: #10243a;
        border: 1px solid #294663;
        border-radius: 18px;
        padding: 18px;
        min-height: 130px;
    }

    .metric-label {
        color: #a9c0d8;
        font-size: 14px;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 30px;
        font-weight: 750;
    }

    .metric-help {
        color: #8fcaff;
        font-size: 13px;
        margin-top: 8px;
    }

    .alert-high {
        background: #301b2c;
        border: 1px solid #e54861;
        border-radius: 18px;
        padding: 22px;
        margin: 22px 0;
    }

    .alert-medium {
        background: #3b3517;
        border: 1px solid #d6b43c;
        border-radius: 18px;
        padding: 22px;
        margin: 22px 0;
    }

    .alert-low {
        background: #12352c;
        border: 1px solid #36b37e;
        border-radius: 18px;
        padding: 22px;
        margin: 22px 0;
    }

    .rain-card {
        background: linear-gradient(135deg, #12385a, #174b70);
        border: 1px solid #39759d;
        border-radius: 18px;
        padding: 24px;
        margin: 18px 0;
    }

    .rain-card h3 {
        margin-top: 0;
    }

    .rain-time {
        font-size: 27px;
        font-weight: 750;
        color: #ffffff;
        margin: 10px 0;
    }

    .small-muted {
        color: #9db3ca;
        font-size: 13px;
    }

    .sidebar-title {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .sidebar-subtitle {
        color: #91a8c0;
        font-size: 14px;
        margin-bottom: 28px;
    }

    div[data-testid="stMetric"] {
        background: #10243a;
        border: 1px solid #294663;
        border-radius: 18px;
        padding: 15px;
    }

    div[data-testid="stMetricLabel"] {
        color: #a9c0d8;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
    }

    div[data-testid="stTabs"] button {
        color: #d7e8fa;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #ff6680;
    }

    .stButton > button {
        border-radius: 12px;
        border: 1px solid #3d78a5;
        background: #174878;
        color: white;
        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #67b7e8;
        background: #205d8c;
    }

    .stChatMessage {
        background: #10243a;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CITY DATA
# =========================================================

CITIES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
}


# =========================================================
# WEATHER CODE
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
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def weather_description(code):
    return WEATHER_CODES.get(int(code), "Unknown condition")


# =========================================================
# API
# =========================================================

@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(city):
    lat = CITIES[city]["lat"]
    lon = CITIES[city]["lon"]

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "is_day,precipitation,rain,weather_code,cloud_cover,"
            "pressure_msl,wind_speed_10m,wind_direction_10m"
        ),
        "hourly": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation_probability,precipitation,rain,weather_code,"
            "cloud_cover,wind_speed_10m,wind_gusts_10m"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "apparent_temperature_max,apparent_temperature_min,"
            "sunrise,sunset,precipitation_sum,rain_sum,"
            "precipitation_probability_max,wind_speed_10m_max"
        ),
        "timezone": "auto",
        "forecast_days": 7,
        "past_days": 0,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def prepare_hourly(data):
    hourly = data["hourly"]

    df = pd.DataFrame(hourly)
    df["time"] = pd.to_datetime(df["time"])

    return df


def prepare_daily(data):
    daily = data["daily"]

    df = pd.DataFrame(daily)
    df["time"] = pd.to_datetime(df["time"])

    return df


# =========================================================
# HISTORICAL DATA
# =========================================================

@st.cache_data
def load_historical_data():
    possible_paths = [
        "data/weather.csv",
        "./data/weather.csv",
        "weather.csv",
        "./weather.csv",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)

                required = [
                    "date",
                    "location",
                    "temperature",
                    "humidity",
                    "rainfall",
                    "wind_speed",
                ]

                if all(col in df.columns for col in required):
                    df["date"] = pd.to_datetime(df["date"])
                    return df

            except Exception:
                return None

    return None


# =========================================================
# OPTIONAL ML MODEL
# =========================================================

@st.cache_resource
def load_rainfall_model():
    if joblib is None:
        return None

    possible_paths = [
        "rainfall_model.pkl",
        "./rainfall_model.pkl",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                return joblib.load(path)
            except Exception:
                return None

    return None


def predict_rainfall(data, historical_df=None):
    """
    Uses rainfall_model.pkl if available.
    Otherwise uses a transparent fallback estimate.
    """

    current = data["current"]

    temperature = float(current.get("temperature_2m", 0))
    humidity = float(current.get("relative_humidity_2m", 0))
    wind = float(current.get("wind_speed_10m", 0))

    model = load_rainfall_model()

    if model is not None:
        try:
            features = np.array([[temperature, humidity, wind]])
            prediction = float(model.predict(features)[0])
            return max(0.0, prediction), "Machine-learning model"
        except Exception:
            pass

    hourly = prepare_hourly(data)

    rain_probability = hourly["precipitation_probability"].head(24).max()
    rain_sum = hourly["rain"].head(24).sum()

    estimated = max(
        float(rain_sum),
        float(rain_probability) * 0.25,
    )

    return round(estimated, 1), "Weather-based estimate"


# =========================================================
# RAIN TIMING
# =========================================================

def get_rain_timing(hourly):
    """
    Finds the first continuous rain window.
    Timing is an estimate from the hourly forecast.
    """

    df = hourly.copy()

    now = pd.Timestamp.now(tz=df["time"].dt.tz)

    future = df[df["time"] >= now].head(48).copy()

    if future.empty:
        return None

    rain_mask = (
        (future["precipitation_probability"] >= 40)
        | (future["precipitation"] > 0)
        | (future["rain"] > 0)
    )

    rain_indices = list(future.index[rain_mask])

    if not rain_indices:
        return None

    start_index = rain_indices[0]
    start_position = future.index.get_loc(start_index)

    end_position = start_position

    for i in range(start_position + 1, len(future)):
        row = future.iloc[i]

        is_rain = (
            row["precipitation_probability"] >= 40
            or row["precipitation"] > 0
            or row["rain"] > 0
        )

        if is_rain:
            end_position = i
        else:
            break

    start_time = future.iloc[start_position]["time"]
    end_time = future.iloc[end_position]["time"]

    duration_hours = max(
        1,
        int((end_time - start_time).total_seconds() / 3600) + 1,
    )

    window = future.iloc[start_position : end_position + 1]

    max_rain = float(window["precipitation"].max())
    max_probability = float(window["precipitation_probability"].max())

    if max_rain >= 5:
        intensity = "Heavy"
    elif max_rain >= 2:
        intensity = "Moderate"
    else:
        intensity = "Light"

    return {
        "start": start_time,
        "end": end_time,
        "duration": duration_hours,
        "intensity": intensity,
        "probability": max_probability,
        "rain_mm": max_rain,
    }


# =========================================================
# RISK ASSESSMENT
# =========================================================

def calculate_risk(data):
    current = data["current"]
    hourly = prepare_hourly(data)

    rain_probability = float(
        hourly["precipitation_probability"].head(24).max()
    )

    wind = float(current.get("wind_speed_10m", 0))
    weather_code = int(current.get("weather_code", 0))

    rain_score = min(45, rain_probability * 0.45)
    wind_score = min(25, wind * 1.5)

    thunder_score = (
        25
        if weather_code in [95, 96, 99]
        else 0
    )

    score = int(min(100, rain_score + wind_score + thunder_score))

    if score >= 70:
        level = "High"
        color = "high"
        message = (
            "Heavy rain, strong wind or thunderstorm conditions "
            "may affect outdoor activities."
        )
    elif score >= 40:
        level = "Moderate"
        color = "medium"
        message = (
            "Rain or changing weather conditions are possible. "
            "Plan outdoor activities carefully."
        )
    else:
        level = "Low"
        color = "low"
        message = (
            "Weather conditions look relatively stable. "
            "Normal outdoor activities are suitable."
        )

    return {
        "score": score,
        "level": level,
        "color": color,
        "message": message,
    }


# =========================================================
# CHARTS
# =========================================================

def hourly_chart(hourly):
    df = hourly.head(24).copy()

    df["time_label"] = df["time"].dt.strftime("%I %p")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["time_label"],
            y=df["temperature_2m"],
            mode="lines+markers",
            name="Temperature",
            line=dict(color="#ff9f43", width=3),
            marker=dict(size=7),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["time_label"],
            y=df["apparent_temperature"],
            mode="lines",
            name="Feels like",
            line=dict(color="#8ec5ff", width=2, dash="dot"),
        )
    )

    fig.update_layout(
        title="Next 24 hours",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        template="plotly_dark",
        height=390,
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(orientation="h"),
    )

    return fig


def rain_probability_chart(hourly):
    df = hourly.head(24).copy()
    df["time_label"] = df["time"].dt.strftime("%I %p")

    fig = px.bar(
        df,
        x="time_label",
        y="precipitation_probability",
        labels={
            "time_label": "Time",
            "precipitation_probability": "Rain probability (%)",
        },
        title="Hourly rain probability",
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=55, b=10),
    )

    return fig


def seven_day_chart(daily):
    df = daily.head(7).copy()
    df["day"] = df["time"].dt.strftime("%a")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["day"],
            y=df["temperature_2m_max"],
            name="Maximum",
            marker_color="#ff9f43",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df["day"],
            y=df["temperature_2m_min"],
            name="Minimum",
            marker_color="#5dade2",
        )
    )

    fig.update_layout(
        title="7-day temperature forecast",
        xaxis_title="Day",
        yaxis_title="Temperature (°C)",
        barmode="group",
        template="plotly_dark",
        height=380,
        margin=dict(l=10, r=10, t=55, b=10),
    )

    return fig


def historical_chart(df, city):
    city_df = df[df["location"].str.lower() == city.lower()].copy()

    if city_df.empty:
        return None

    city_df = city_df.sort_values("date")

    fig = px.line(
        city_df,
        x="date",
        y="rainfall",
        markers=True,
        title=f"Historical rainfall — {city}",
        labels={
            "date": "Date",
            "rainfall": "Rainfall (mm)",
        },
    )

    fig.update_layout(
        template="plotly_dark",
        height=380,
        margin=dict(l=10, r=10, t=55, b=10),
    )

    return fig


def historical_temperature_chart(df, city):
    city_df = df[df["location"].str.lower() == city.lower()].copy()

    if city_df.empty:
        return None

    city_df = city_df.sort_values("date")

    fig = px.line(
        city_df,
        x="date",
        y="temperature",
        markers=True,
        title=f"Historical temperature — {city}",
        labels={
            "date": "Date",
            "temperature": "Temperature (°C)",
        },
    )

    fig.update_layout(
        template="plotly_dark",
        height=380,
        margin=dict(l=10, r=10, t=55, b=10),
    )

    return fig


# =========================================================
# MAP
# =========================================================

def create_risk_map(selected_city, risk):
    """
    Plotly map — no Folium dependency required.
    """

    locations = []

    for city, coords in CITIES.items():
        if city == selected_city:
            locations.append(
                {
                    "city": city,
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "risk": risk["level"],
                    "score": risk["score"],
                    "selected": "Selected location",
                }
            )
        else:
            locations.append(
                {
                    "city": city,
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "risk": "Reference",
                    "score": 0,
                    "selected": "Other location",
                }
            )

    df = pd.DataFrame(locations)

    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        hover_name="city",
        hover_data=["risk", "score"],
        color="selected",
        size="score",
        zoom=3.6,
        center={
            "lat": 22.5,
            "lon": 79.0,
        },
        height=500,
        title="WeatherNex risk map",
    )

    fig.update_layout(
        map_style="open-street-map",
        margin=dict(l=0, r=0, t=55, b=0),
    )

    return fig


# =========================================================
# ADVICE
# =========================================================

def get_recommendations(data, risk, rain_timing):
    current = data["current"]
    hourly = prepare_hourly(data)

    temperature = float(current.get("temperature_2m", 0))
    wind = float(current.get("wind_speed_10m", 0))
    rain_probability = float(
        hourly["precipitation_probability"].head(24).max()
    )

    recommendations = []

    if rain_probability >= 60:
        recommendations.append(
            "☔ Carry an umbrella or raincoat."
        )

    if temperature >= 35:
        recommendations.append(
            "🥤 Stay hydrated and avoid prolonged exposure to heat."
        )

    if temperature <= 15:
        recommendations.append(
            "🧥 Carry a light jacket if you are going outdoors."
        )

    if wind >= 30:
        recommendations.append(
            "🌬️ Avoid unsafe outdoor activities during strong winds."
        )

    if rain_timing:
        recommendations.append(
            "📅 Keep outdoor plans flexible around the expected rain window."
        )

    if not recommendations:
        recommendations.append(
            "🌤️ Weather looks suitable for normal outdoor activities."
        )

    return recommendations


# =========================================================
# COPILOT
# =========================================================

def copilot_response(question, city, data, risk, rain_timing):
    q = question.lower().strip()

    current = data["current"]
    hourly = prepare_hourly(data)
    daily = prepare_daily(data)

    temperature = float(current.get("temperature_2m", 0))
    feels_like = float(current.get("apparent_temperature", 0))
    humidity = float(current.get("relative_humidity_2m", 0))
    wind = float(current.get("wind_speed_10m", 0))

    rain_probability = float(
        hourly["precipitation_probability"].head(24).max()
    )

    if any(word in q for word in ["rain", "baarish", "barish"]):
        if rain_timing:
            return (
                f"🌧️ **{city} mein rain ka forecast hai.**\n\n"
                f"Expected start: **{rain_timing['start'].strftime('%I:%M %p')}**\n\n"
                f"Expected end: **{rain_timing['end'].strftime('%I:%M %p')}**\n\n"
                f"Estimated duration: **{rain_timing['duration']} hour(s)**\n\n"
                f"Intensity: **{rain_timing['intensity']}**\n\n"
                f"Rain probability: **{rain_timing['probability']:.0f}%**\n\n"
                "Ye hourly forecast par based estimate hai; weather update "
                "hone par timing change ho sakti hai."
            )

        return (
            f"🌤️ **{city} mein agle 24 hours mein significant rain "
            f"ka forecast nahi dikh raha.**\n\n"
            f"Maximum rain probability: **{rain_probability:.0f}%**"
        )

    if any(word in q for word in ["temperature", "temp", "garmi", "thand"]):
        return (
            f"🌡️ **{city} ka current temperature {temperature:.1f}°C hai.**\n\n"
            f"Feels like: **{feels_like:.1f}°C**\n\n"
            f"Humidity: **{humidity:.0f}%**\n\n"
            f"Wind speed: **{wind:.1f} km/h**"
        )

    if any(word in q for word in ["umbrella", "chhatri", "carry"]):
        if rain_probability >= 50:
            return (
                f"☔ Haan, **umbrella carry karna better rahega**. "
                f"Next 24 hours mein rain probability **{rain_probability:.0f}%** hai."
            )

        return (
            "🌤️ Abhi umbrella ki strong need nahi lag rahi, "
            "lekin outdoor plan long hai toh carry kar sakte ho."
        )

    if any(word in q for word in ["tomorrow", "kal"]):
        tomorrow = daily.iloc[1]

        return (
            f"📅 **Kal {city} ka forecast:**\n\n"
            f"Temperature: **{tomorrow['temperature_2m_min']:.1f}°C – "
            f"{tomorrow['temperature_2m_max']:.1f}°C**\n\n"
            f"Rain probability: **{tomorrow['precipitation_probability_max']:.0f}%**\n\n"
            f"Condition: **{weather_description(tomorrow['weather_code'])}**"
        )

    if any(word in q for word in ["risk", "safe", "danger", "alert"]):
        return (
            f"⚠️ **Weather risk level: {risk['level']}**\n\n"
            f"Risk score: **{risk['score']}/100**\n\n"
            f"{risk['message']}"
        )

    if any(word in q for word in ["plan", "outing", "outdoor", "bahar"]):
        if risk["level"] == "High":
            return (
                "⚠️ Outdoor plan postpone karna better rahega, "
                "especially rain ya thunderstorm ke time."
            )

        if risk["level"] == "Moderate":
            return (
                "🌦️ Outdoor plan kar sakte ho, lekin umbrella carry karo "
                "aur weather updates check karte raho."
            )

        return (
            "🌤️ Weather outdoor activities ke liye relatively suitable hai."
        )

    if any(word in q for word in ["wind", "hawa", "humidity"]):
        return (
            f"🌬️ Current wind speed: **{wind:.1f} km/h**\n\n"
            f"💧 Humidity: **{humidity:.0f}%**"
        )

    return (
        f"🌦️ **{city} Weather Copilot**\n\n"
        f"Current temperature: **{temperature:.1f}°C**\n\n"
        f"Rain probability: **{rain_probability:.0f}%**\n\n"
        f"Risk level: **{risk['level']}**\n\n"
        "Aap rain timing, temperature, umbrella, tomorrow forecast, "
        "outdoor plan ya risk ke baare mein pooch sakte ho."
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-title">🌦️ WeatherNex</div>
        <div class="sidebar-subtitle">
            National Weather Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### 📍 Select Location")

    city = st.selectbox(
        "Choose city",
        list(CITIES.keys()),
        index=0,
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("🔄 Refresh Weather", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.markdown("### 🧠 Intelligence Modules")

    st.markdown(
        """
        🌐 Live Weather

        📊 Historical Analysis

        🤖 AI Rainfall Prediction

        ⚠️ Risk Assessment

        🗺️ Risk Map

        🕒 Hourly Forecast

        📅 7-Day Forecast

        🚨 Early Warning

        💬 Weather Copilot
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LOAD DATA
# =========================================================

try:
    weather_data = fetch_weather(city)
    hourly = prepare_hourly(weather_data)
    daily = prepare_daily(weather_data)
    current = weather_data["current"]

except Exception as e:
    st.error(f"Weather data load nahi ho paaya: {e}")
    st.stop()


risk = calculate_risk(weather_data)
rain_timing = get_rain_timing(hourly)
historical_df = load_historical_data()


# =========================================================
# HERO
# =========================================================

st.markdown(
    f"""
    <div class="hero">
        <h1>🌦️ WeatherNex</h1>
        <p>National Weather Intelligence Platform</p>
        <p>
            📍 {city}
            &nbsp; • &nbsp;
            {weather_description(current["weather_code"])}
            &nbsp; • &nbsp;
            🕒 Live forecast
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# TABS
# =========================================================

tabs = st.tabs(
    [
        "📊 Overview",
        "🕒 Hourly Forecast",
        "📅 7-Day Forecast",
        "🗺️ Risk Map",
        "📈 Historical Analysis",
        "🚨 Early Warning",
        "💬 Weather Copilot",
    ]
)


# =========================================================
# OVERVIEW
# =========================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">🌤️ Current Weather</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Live weather conditions and real-time intelligence</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "🌡️ Temperature",
            f"{current['temperature_2m']:.1f}°C",
            f"Feels like {current['apparent_temperature']:.1f}°C",
        )

    with c2:
        st.metric(
            "🌧️ Rain probability",
            f"{hourly['precipitation_probability'].head(24).max():.0f}%",
            "Next 24 hours",
        )

    with c3:
        st.metric(
            "💧 Humidity",
            f"{current['relative_humidity_2m']:.0f}%",
            "Relative humidity",
        )

    with c4:
        st.metric(
            "🌬️ Wind speed",
            f"{current['wind_speed_10m']:.1f}",
            "km/h",
        )

    with c5:
        st.metric(
            "⚠️ Risk level",
            risk["level"],
            f"Score {risk['score']}/100",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="info-card">
            <h3>🌤️ Current Conditions</h3>
            <p>
                <b>{weather_description(current['weather_code'])}</b>
                &nbsp; • &nbsp;
                Cloud cover: <b>{current['cloud_cover']}%</b>
                &nbsp; • &nbsp;
                Pressure: <b>{current['pressure_msl']} hPa</b>
                &nbsp; • &nbsp;
                Precipitation: <b>{current['precipitation']} mm</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Risk alert
    st.markdown(
        f"""
        <div class="alert-{risk['color']}">
            <h3>⚠️ {risk['level']} Weather Risk</h3>
            <p>{risk['message']}</p>
            <p><b>Risk score: {risk['score']}/100</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Rain timing
    st.markdown(
        '<div class="section-title">🌧️ Rain Timing Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Estimated rain start, end and duration from the hourly forecast</div>',
        unsafe_allow_html=True,
    )

    if rain_timing:

        st.markdown(
            f"""
            <div class="rain-card">
                <h3>🌧️ Rain expected in {city}</h3>
                <div class="rain-time">
                    {rain_timing['start'].strftime('%I:%M %p')}
                    →
                    {rain_timing['end'].strftime('%I:%M %p')}
                </div>
                <p>
                    Estimated duration:
                    <b>{rain_timing['duration']} hour(s)</b>
                    <br>
                    Intensity:
                    <b>{rain_timing['intensity']}</b>
                    <br>
                    Probability:
                    <b>{rain_timing['probability']:.0f}%</b>
                    <br>
                    Expected rainfall:
                    <b>{rain_timing['rain_mm']:.1f} mm</b>
                </p>
                <p class="small-muted">
                    Note: Rain timing is an estimate based on the hourly forecast.
                    It may change with new weather updates.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="info-card">
                <h3>🌤️ No significant rain window detected</h3>
                <p>
                    The next 48 hours do not currently show a continuous
                    rain window above the selected forecast threshold.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Quick charts
    st.markdown(
        '<div class="section-title">📊 Weather Trends</div>',
        unsafe_allow_html=True,
    )

    chart1, chart2 = st.columns(2)

    with chart1:
        st.plotly_chart(
            hourly_chart(hourly),
            use_container_width=True,
            key="overview_hourly_chart",
        )

    with chart2:
        st.plotly_chart(
            rain_probability_chart(hourly),
            use_container_width=True,
            key="overview_rain_chart",
        )

    # Recommendations
    st.markdown(
        '<div class="section-title">💡 Recommended Actions</div>',
        unsafe_allow_html=True,
    )

    recommendations = get_recommendations(
        weather_data,
        risk,
        rain_timing,
    )

    for recommendation in recommendations:
        st.info(recommendation)


# =========================================================
# HOURLY FORECAST
# =========================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">🕒 Hourly Forecast</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Detailed weather conditions for the next 24 hours</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        hourly_chart(hourly),
        use_container_width=True,
        key="hourly_tab_temperature_chart",
    )

    st.plotly_chart(
        rain_probability_chart(hourly),
        use_container_width=True,
        key="hourly_tab_rain_chart",
    )

    display_hourly = hourly.head(24).copy()

    display_hourly["Time"] = display_hourly["time"].dt.strftime(
        "%d %b, %I:%M %p"
    )

    display_hourly = display_hourly[
        [
            "Time",
            "temperature_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "relative_humidity_2m",
            "wind_speed_10m",
        ]
    ]

    display_hourly.columns = [
        "Time",
        "Temperature (°C)",
        "Feels like (°C)",
        "Rain probability (%)",
        "Rainfall (mm)",
        "Humidity (%)",
        "Wind speed (km/h)",
    ]

    st.dataframe(
        display_hourly,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# 7-DAY FORECAST
# =========================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">📅 7-Day Forecast</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Temperature, rainfall and daily weather conditions</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        seven_day_chart(daily),
        use_container_width=True,
        key="seven_day_temperature_chart",
    )

    display_daily = daily.head(7).copy()

    display_daily["Day"] = display_daily["time"].dt.strftime("%A")

    display_daily["Condition"] = display_daily["weather_code"].apply(
        weather_description
    )

    display_daily = display_daily[
        [
            "Day",
            "Condition",
            "temperature_2m_min",
            "temperature_2m_max",
            "precipitation_probability_max",
            "precipitation_sum",
            "wind_speed_10m_max",
        ]
    ]

    display_daily.columns = [
        "Day",
        "Condition",
        "Min temp (°C)",
        "Max temp (°C)",
        "Rain probability (%)",
        "Rainfall (mm)",
        "Max wind (km/h)",
    ]

    st.dataframe(
        display_daily,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# RISK MAP
# =========================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">🗺️ Weather Risk Map</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Selected location and reference locations across India</div>',
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        create_risk_map(city, risk),
        use_container_width=True,
        key="weather_risk_map",
    )

    st.info(
        "The selected city is highlighted using the current risk score. "
        "Other locations are shown as reference points."
    )


# =========================================================
# HISTORICAL ANALYSIS
# =========================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">📈 Historical Rainfall Analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Historical trends from your uploaded weather dataset</div>',
        unsafe_allow_html=True,
    )

    if historical_df is None:

        st.warning(
            "Historical dataset nahi mila. "
            "Apni CSV file ko exactly `data/weather.csv` naam se rakho."
        )

        st.code(
            "newweathernex/\n"
            "├── app_backup.py\n"
            "├── requirements.txt\n"
            "├── rainfall_model.pkl\n"
            "└── data/\n"
            "    └── weather.csv"
        )

    else:

        city_history = historical_df[
            historical_df["location"].str.lower() == city.lower()
        ].copy()

        if city_history.empty:

            st.warning(
                f"Historical dataset mein {city} ka data available nahi hai."
            )

        else:

            avg_rainfall = city_history["rainfall"].mean()
            total_rainfall = city_history["rainfall"].sum()
            max_rainfall = city_history["rainfall"].max()

            h1, h2, h3 = st.columns(3)

            with h1:
                st.metric(
                    "📊 Historical average",
                    f"{avg_rainfall:.1f} mm",
                )

            with h2:
                st.metric(
                    "🌧️ Total rainfall",
                    f"{total_rainfall:.1f} mm",
                )

            with h3:
                st.metric(
                    "📈 Maximum rainfall",
                    f"{max_rainfall:.1f} mm",
                )

            hc1, hc2 = st.columns(2)

            with hc1:
                fig = historical_chart(historical_df, city)

                if fig is not None:
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key="historical_rainfall_chart",
                    )

            with hc2:
                fig = historical_temperature_chart(
                    historical_df,
                    city,
                )

                if fig is not None:
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key="historical_temperature_chart",
                    )

            st.dataframe(
                city_history.sort_values("date", ascending=False),
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# EARLY WARNING + AI RAINFALL PREDICTION
# =========================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">🚨 Early Warning & AI Rainfall Prediction</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Weather-based intelligence and rainfall estimation</div>',
        unsafe_allow_html=True,
    )

    predicted_rainfall, prediction_source = predict_rainfall(
        weather_data,
        historical_df,
    )

    if historical_df is not None:

        city_history = historical_df[
            historical_df["location"].str.lower() == city.lower()
        ]

        historical_average = (
            float(city_history["rainfall"].mean())
            if not city_history.empty
            else 0.0
        )

    else:
        historical_average = 0.0

    if historical_average > 0:
        deviation = (
            (predicted_rainfall - historical_average)
            / historical_average
        ) * 100
    else:
        deviation = 0.0

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric(
            "🌧️ Predicted rainfall",
            f"{predicted_rainfall:.1f} mm",
        )

    with p2:
        st.metric(
            "📊 Historical average",
            f"{historical_average:.1f} mm",
        )

    with p3:
        st.metric(
            "📈 Deviation from average",
            f"{deviation:.1f}%",
        )

    st.caption(
        f"Prediction source: {prediction_source}"
    )

    st.markdown(
        f"""
        <div class="alert-{risk['color']}">
            <h3>⚠️ Weather Risk Assessment</h3>
            <p>
                Rainfall risk: <b>{risk['level'].upper()}</b>
            </p>
            <p>
                {risk['message']}
            </p>
            <p>
                Risk score: <b>{risk['score']}/100</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rain_timing:

        st.markdown(
            f"""
            <div class="rain-card">
                <h3>🌧️ Smart Rain Alert</h3>
                <p>
                    Rain may start around
                    <b>{rain_timing['start'].strftime('%I:%M %p')}</b>
                    and continue until approximately
                    <b>{rain_timing['end'].strftime('%I:%M %p')}</b>.
                </p>
                <p>
                    Estimated duration:
                    <b>{rain_timing['duration']} hour(s)</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.success(
            "No significant continuous rain window detected in the next 48 hours."
        )


# =========================================================
# WEATHER COPILOT
# =========================================================

with tabs[6]:

    st.markdown(
        '<div class="section-title">💬 Weather Copilot</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">Ask questions about the live weather forecast</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Try asking: Rain kab start hogi? | Kal weather kaisa rahega? | "
        "Umbrella carry karu? | Is it safe to go outside?"
    )

    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = []

    for message in st.session_state.copilot_messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask Weather Copilot..."
    )

    if question:

        st.session_state.copilot_messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        answer = copilot_response(
            question,
            city,
            weather_data,
            risk,
            rain_timing,
        )

        st.session_state.copilot_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <br><br>
    <div style="
        text-align:center;
        color:#7890a8;
        font-size:13px;
        padding:20px;
        border-top:1px solid #203b57;
    ">
        WeatherNex • Weather Intelligence Platform
        <br>
        Live forecast powered by Open-Meteo
    </div>
    """,
    unsafe_allow_html=True,
)
