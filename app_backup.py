import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
import joblib
import folium
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
# BEAUTIFUL UI
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(37,99,235,.18), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(14,165,233,.12), transparent 25%),
        #08111f;
    color: #e5edf7;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1500px;
    padding: 2rem 2.5rem 4rem;
}

[data-testid="stSidebar"] {
    background: #0b1728;
    border-right: 1px solid #1e334c;
}

[data-testid="stSidebar"] * {
    color: #dbeafe !important;
}

.hero {
    background: linear-gradient(135deg, #102a4b, #123b61 55%, #0e7490);
    border: 1px solid #28577d;
    border-radius: 28px;
    padding: 32px;
    margin-bottom: 30px;
    box-shadow: 0 15px 45px rgba(0,0,0,.18);
}

.hero h1 {
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0;
    color: white;
}

.hero p {
    color: #c7e3fa;
    margin: 8px 0 0;
}

.section-title {
    font-size: 1.35rem;
    font-weight: 750;
    margin-top: 38px;
    margin-bottom: 20px;
    color: #f1f5f9;
}

.metric-card {
    background: linear-gradient(145deg, #12243a, #0e1b2c);
    border: 1px solid #294866;
    border-radius: 20px;
    padding: 22px;
    min-height: 135px;
    box-shadow: 0 8px 25px rgba(0,0,0,.12);
}

.metric-label {
    color: #8fa8c2;
    font-size: .85rem;
    font-weight: 600;
}

.metric-value {
    color: #f8fafc;
    font-size: 2rem;
    font-weight: 800;
    margin-top: 10px;
}

.metric-sub {
    color: #93c5fd;
    font-size: .78rem;
    margin-top: 5px;
}

.info-card {
    background: #101f32;
    border: 1px solid #294866;
    border-radius: 20px;
    padding: 24px;
    margin-top: 0;
    margin-bottom: 22px;
}

.info-card h3 {
    margin: 0 0 14px;
    color: #f8fafc;
    font-size: 1.05rem;
}

.info-card p {
    color: #b8c9dc;
    line-height: 1.7;
    margin: 0;
}

.rain-card {
    background: linear-gradient(135deg, #123b61, #164e63);
    border: 1px solid #2d759b;
    border-radius: 22px;
    padding: 25px;
    margin-top: 28px;
    margin-bottom: 30px;
}

.rain-card h2 {
    margin: 0;
    color: white;
}

.rain-card .big {
    font-size: 2.4rem;
    font-weight: 800;
    color: #bae6fd;
    margin: 12px 0;
}

.alert-card,
.success-card,
.danger-card {
    border-radius: 18px;
    padding: 18px 22px;
    margin-top: 24px;
    margin-bottom: 28px;
}

.alert-card {
    border: 1px solid #f59e0b;
    background: rgba(245,158,11,.10);
}

.success-card {
    border: 1px solid #22c55e;
    background: rgba(34,197,94,.10);
}

.danger-card {
    border: 1px solid #ef4444;
    background: rgba(239,68,68,.10);
}

.alert-card h3,
.success-card h3,
.danger-card h3 {
    margin: 0 0 8px;
}

.alert-card p,
.success-card p,
.danger-card p {
    margin: 0;
    line-height: 1.6;
}

div[data-testid="stMetric"] {
    background: #101f32;
    border: 1px solid #243d58;
    border-radius: 18px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #8fa8c2;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #0e1b2c;
    border-radius: 14px;
    padding: 6px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 18px;
}

.stTabs [aria-selected="true"] {
    background: #2563eb;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid #315b82;
    background: #163657;
    color: white;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: #60a5fa;
    background: #1d4f7a;
}

.stChatMessage {
    background: #101f32;
    border: 1px solid #243d58;
    border-radius: 15px;
}

hr {
    border-color: #243d58;
}

@media (max-width: 700px) {
    .block-container {
        padding: 1rem;
    }

    .hero {
        padding: 24px;
    }

    .hero h1 {
        font-size: 1.7rem;
    }

    .metric-card {
        padding: 16px;
        min-height: 120px;
    }

    .section-title {
        margin-top: 28px;
        margin-bottom: 16px;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOCATIONS
# =========================================================

locations = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Ahmedabad": (23.0225, 72.5714),
    "Chandigarh": (30.7333, 76.7794),
    "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376),
    "Bhubaneswar": (20.2961, 85.8245),
    "Guwahati": (26.1445, 91.7362)
}

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate showers",
    82: "Heavy showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Heavy thunderstorm"
}

def weather_description(code):
    return WEATHER_CODES.get(int(code), "Unknown weather")

def safe_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# =========================================================
# WEATHER API
# =========================================================

@st.cache_data(ttl=600, show_spinner=False)
def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "wind_speed_10m",
            "surface_pressure"
        ]),
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation_probability",
            "precipitation",
            "rain",
            "weather_code",
            "wind_speed_10m",
            "cloud_cover",
            "visibility"
        ]),
        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "sunrise",
            "sunset",
            "wind_speed_10m_max"
        ]),
        "forecast_days": 7,
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

def prepare_hourly(data):
    h = data["hourly"]

    return pd.DataFrame({
        "time": pd.to_datetime(h["time"]),
        "temperature": h["temperature_2m"],
        "humidity": h["relative_humidity_2m"],
        "rain_probability": h["precipitation_probability"],
        "precipitation": h["precipitation"],
        "rain": h["rain"],
        "weather_code": h["weather_code"],
        "wind": h["wind_speed_10m"],
        "cloud": h["cloud_cover"],
        "visibility": h["visibility"]
    })

def prepare_daily(data):
    d = data["daily"]

    return pd.DataFrame({
        "date": pd.to_datetime(d["time"]),
        "weather_code": d["weather_code"],
        "max_temp": d["temperature_2m_max"],
        "min_temp": d["temperature_2m_min"],
        "rainfall": d["precipitation_sum"],
        "rain_probability": d["precipitation_probability_max"],
        "sunrise": d["sunrise"],
        "sunset": d["sunset"],
        "max_wind": d["wind_speed_10m_max"]
    })

# =========================================================
# RAIN TIMING
# =========================================================

def get_rain_timing(hourly):
    """
    Estimates the first continuous rain window from the
    hourly forecast. It is not an exact guarantee.
    """

    now = pd.Timestamp.now(tz=hourly["time"].dt.tz)

    future = hourly[hourly["time"] >= now].head(48).copy()

    if future.empty:
        return None

    rain_mask = (
        (future["rain_probability"].fillna(0) >= 40) |
        (future["precipitation"].fillna(0) > 0.1) |
        (future["rain"].fillna(0) > 0.1)
    )

    rain_hours = future[rain_mask]

    if rain_hours.empty:
        return None

    start_index = rain_hours.index[0]
    start_pos = future.index.get_loc(start_index)
    end_pos = start_pos

    for i in range(start_pos + 1, len(future)):
        row = future.iloc[i]

        is_rain = (
            safe_float(row["rain_probability"]) >= 40 or
            safe_float(row["precipitation"]) > 0.1 or
            safe_float(row["rain"]) > 0.1
        )

        if is_rain:
            end_pos = i
        else:
            break

    window = future.iloc[start_pos:end_pos + 1]

    start_time = window["time"].iloc[0]
    end_time = window["time"].iloc[-1] + pd.Timedelta(hours=1)

    duration = max(1, int(round(
        (end_time - start_time).total_seconds() / 3600
    )))

    max_rain = safe_float(window["precipitation"].max())
    max_probability = safe_float(window["rain_probability"].max())

    if max_rain >= 5:
        intensity = "Heavy"
    elif max_rain >= 2:
        intensity = "Moderate"
    else:
        intensity = "Light"

    return {
        "start": start_time,
        "end": end_time,
        "duration": duration,
        "intensity": intensity,
        "probability": max_probability,
        "rainfall": max_rain
    }

def format_time(timestamp):
    return timestamp.strftime("%I:%M %p").lstrip("0")

def rain_timing_card(timing):
    if timing is None:
        st.markdown("""
        <div class="success-card">
            <h3>☀️ No significant rain expected</h3>
            <p>The upcoming hourly forecast does not show a continuous rain window.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="rain-card">
        <h2>🌧️ Rain timing forecast</h2>
        <div class="big">{format_time(timing["start"])}</div>
        <p style="color:#dbeafe;font-size:1.1rem;">
            Rain may start around <b>{format_time(timing["start"])}</b>
            and continue until approximately
            <b>{format_time(timing["end"])}</b>.
        </p>
        <hr style="border-color:#3b6b8d;">
        <p style="color:#dbeafe;">
            ⏱️ <b>Duration:</b> {timing["duration"]} hour(s)
            &nbsp;&nbsp;|&nbsp;&nbsp;
            ☔ <b>Intensity:</b> {timing["intensity"]}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            📊 <b>Probability:</b> {timing["probability"]:.0f}%
        </p>
        <p style="color:#93c5fd;font-size:.8rem;margin-top:12px;">
            This is an estimate from the hourly weather forecast, not an exact guarantee.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# HISTORICAL DATA + ML
# =========================================================

@st.cache_data(show_spinner=False)
def load_historical_data():
    try:
        df = pd.read_csv("data/weather.csv")
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception:
        return None

@st.cache_resource(show_spinner=False)
def load_model():
    try:
        return joblib.load("rainfall_model.pkl")
    except Exception:
        return None

def get_prediction(model, temperature, humidity, wind_speed):
    if model is None:
        return None

    try:
        model_input = pd.DataFrame({
            "temperature": [temperature],
            "humidity": [humidity],
            "wind_speed": [wind_speed]
        })

        prediction = model.predict(model_input)[0]
        return max(0, safe_float(prediction))

    except Exception:
        return None

# =========================================================
# RISK + ALERTS
# =========================================================

def calculate_risk(current, hourly):
    max_rain_probability = safe_float(
        hourly["rain_probability"].head(24).max()
    )
    max_wind = safe_float(hourly["wind"].head(24).max())

    thunderstorm = hourly["weather_code"].head(24).isin(
        [95, 96, 99]
    ).any()

    score = 0

    if max_rain_probability >= 70:
        score += 45
    elif max_rain_probability >= 40:
        score += 25
    elif max_rain_probability >= 20:
        score += 10

    if max_wind >= 40:
        score += 30
    elif max_wind >= 25:
        score += 15

    if thunderstorm:
        score += 25

    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MODERATE"
    else:
        level = "LOW"

    return {
        "score": min(score, 100),
        "level": level,
        "rain_probability": max_rain_probability,
        "wind": max_wind,
        "thunderstorm": thunderstorm
    }

def show_alert(risk):
    if risk["level"] == "HIGH":
        st.markdown("""
        <div class="danger-card">
            <h3>🔴 High weather risk</h3>
            <p>
                Heavy rain, strong wind or thunderstorm conditions may affect
                outdoor activities. Stay alert and check updates before travelling.
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif risk["level"] == "MODERATE":
        st.markdown("""
        <div class="alert-card">
            <h3>🟠 Moderate weather risk</h3>
            <p>
                Rain or wind may interrupt outdoor plans.
                Carry an umbrella and keep your travel plans flexible.
            </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="success-card">
            <h3>🟢 Low weather risk</h3>
            <p>
                No major weather disruption is indicated in the upcoming forecast.
            </p>
        </div>
        """, unsafe_allow_html=True)

def get_alert_data(forecast_df, historical_avg):
    max_forecast_rainfall = forecast_df["Rainfall (mm)"].max()

    max_rainfall_date = forecast_df.loc[
        forecast_df["Rainfall (mm)"].idxmax(),
        "Date"
    ]

    avg = max(historical_avg, 1)

    if max_forecast_rainfall > avg * 2:
        return (
            "CRITICAL",
            f"Very heavy rainfall is expected around "
            f"{max_rainfall_date.strftime('%d %b')}. "
            f"Potential waterlogging risk."
        )

    elif max_forecast_rainfall > avg * 1.5:
        return (
            "HIGH",
            f"Heavy rainfall is expected around "
            f"{max_rainfall_date.strftime('%d %b')}. "
            f"Residents should remain alert."
        )

    elif max_forecast_rainfall > avg:
        return (
            "MODERATE",
            f"Rainfall may be above the historical average "
            f"around {max_rainfall_date.strftime('%d %b')}."
        )

    return (
        "LOW",
        "No significant rainfall anomaly detected in the forecast period."
    )

# =========================================================
# MAP
# =========================================================

def create_risk_map(map_df):
    m = folium.Map(
        location=[22.5, 79.0],
        zoom_start=4,
        tiles="OpenStreetMap"
    )

    for _, row in map_df.iterrows():
        risk = row["Risk Level"]

        if risk in ["CRITICAL", "VERY HIGH"]:
            color = "red"
        elif risk == "HIGH":
            color = "orange"
        elif risk == "MODERATE":
            color = "blue"
        else:
            color = "green"

        folium.Marker(
            [row["Latitude"], row["Longitude"]],
            tooltip=row["City"],
            popup=(
                f"<b>{row['City']}</b><br>"
                f"Historical Rainfall: {row['Historical Rainfall']:.1f} mm<br>"
                f"Risk Level: {risk}"
            ),
            icon=folium.Icon(
                color=color,
                icon="cloud",
                prefix="fa"
            )
        ).add_to(m)

    return m

# =========================================================
# CHARTS
# =========================================================

def hourly_chart(hourly):
    df = hourly.head(24).copy()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["temperature"],
        mode="lines+markers",
        name="Temperature °C",
        line=dict(color="#38bdf8", width=3),
        marker=dict(size=7)
    ))

    fig.add_trace(go.Bar(
        x=df["time"],
        y=df["rain_probability"],
        name="Rain probability %",
        marker_color="#2563eb",
        opacity=.35,
        yaxis="y2"
    ))

    fig.update_layout(
        title="Next 24 hours",
        template="plotly_dark",
        height=420,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Time",
        yaxis=dict(title="Temperature °C"),
        yaxis2=dict(
            title="Rain probability %",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        legend=dict(orientation="h", y=1.12),
        hovermode="x unified"
    )

    return fig

def rainfall_chart(hourly):
    df = hourly.head(24).copy()

    fig = px.bar(
        df,
        x="time",
        y="precipitation",
        color="rain_probability",
        color_continuous_scale="Blues",
        title="Hourly precipitation forecast"
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Time",
        yaxis_title="Rainfall (mm)"
    )

    return fig

def daily_chart(daily):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["max_temp"],
        mode="lines+markers",
        name="Maximum temperature",
        line=dict(color="#f59e0b", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["min_temp"],
        mode="lines+markers",
        name="Minimum temperature",
        line=dict(color="#38bdf8", width=3)
    ))

    fig.update_layout(
        title="7-day temperature trend",
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Date",
        yaxis_title="Temperature °C",
        hovermode="x unified"
    )

    return fig

# =========================================================
# DYNAMIC COPILOT
# =========================================================

def copilot_response(question, city, current, hourly, daily, timing, risk):
    q = question.lower().strip()

    temp = safe_float(current["temperature_2m"])
    feels = safe_float(current["apparent_temperature"])
    humidity = safe_float(current["relative_humidity_2m"])
    wind = safe_float(current["wind_speed_10m"])
    rain_prob = risk["rain_probability"]

    if any(word in q for word in ["rain", "barish", "baarish"]):
        if timing:
            return (
                f"🌧️ **{city}** mein rain ka estimated start "
                f"**{format_time(timing['start'])}** ke around hai. "
                f"Ye approximately **{timing['duration']} hour(s)** chal sakti hai "
                f"aur **{format_time(timing['end'])}** tak end hone ka estimate hai. "
                f"Intensity **{timing['intensity'].lower()}** hai."
            )

        return (
            f"☀️ Agle 48 hours ke hourly forecast mein "
            f"**{city}** ke liye koi significant continuous rain window nahi dikh rahi."
        )

    if any(word in q for word in ["umbrella", "chhatri", "bahar", "outdoor"]):
        if rain_prob >= 50:
            return (
                f"☔ Umbrella carry karna better rahega. "
                f"Next 24 hours mein rain probability **{rain_prob:.0f}%** tak hai. "
                f"Outdoor plan ho to rain window ke bahar jaana better hoga."
            )

        return (
            f"🌤️ Outdoor activity ke liye weather comparatively suitable hai. "
            f"Rain probability **{rain_prob:.0f}%** hai."
        )

    if any(word in q for word in ["temperature", "temp", "garmi", "thand"]):
        return (
            f"🌡️ Abhi **{city}** mein temperature **{temp:.1f}°C** hai. "
            f"Feels-like temperature **{feels:.1f}°C** hai, "
            f"humidity **{humidity:.0f}%** aur wind **{wind:.1f} km/h** hai."
        )

    if any(word in q for word in ["tomorrow", "kal"]):
        tomorrow = daily.iloc[1]

        return (
            f"📅 Kal **{city}** mein maximum temperature "
            f"**{tomorrow['max_temp']:.1f}°C** aur minimum "
            f"**{tomorrow['min_temp']:.1f}°C** rehne ka forecast hai. "
            f"Rain probability **{tomorrow['rain_probability']:.0f}%** hai."
        )

    if any(word in q for word in ["risk", "danger", "safe", "alert"]):
        return (
            f"⚠️ Current weather risk **{risk['level']}** hai. "
            f"Risk score **{risk['score']}/100**, "
            f"rain probability **{rain_prob:.0f}%** aur "
            f"maximum wind **{risk['wind']:.1f} km/h** hai."
        )

    if any(word in q for word in ["wind", "hawa", "humidity", "moisture"]):
        return (
            f"💨 Wind speed **{wind:.1f} km/h** hai aur humidity "
            f"**{humidity:.0f}%** hai. "
            f"High humidity ki wajah se temperature actual se zyada uncomfortable feel ho sakta hai."
        )

    if any(word in q for word in ["forecast", "weather", "mausam", "aaj"]):
        return (
            f"🌦️ **{city}** ka current weather: **{temp:.1f}°C**, "
            f"{weather_description(current['weather_code'])}. "
            f"Rain probability **{rain_prob:.0f}%** hai aur weather risk "
            f"**{risk['level']}** hai."
        )

    return (
        f"🤖 Main **{city}** ke current temperature, rain timing, "
        f"hourly forecast, wind, humidity aur risk data ke basis par help kar sakta hoon. "
        f"Try asking: **'Rain kab start hogi?'**, "
        f"**'Kal ka weather?'**, ya **'Umbrella le jaun?'**"
    )

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## 🌦️ WeatherNex")
    st.caption("National Weather Intelligence Platform")

    st.markdown("---")

    location = st.selectbox(
        "📍 Select Location",
        list(locations.keys())
    )

    st.markdown("---")

    if st.button("🔄 Refresh weather", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    st.markdown("### 🧠 Intelligence Modules")

    st.markdown("""
    <div style="line-height:2.1;font-size:15px;">
        🌐 Live Weather<br>
        📊 Historical Analysis<br>
        🤖 AI Rainfall Prediction<br>
        ⚠️ Risk Assessment<br>
        🗺️ Risk Map<br>
        📅 7-Day Forecast<br>
        🔎 Anomaly Detection<br>
        🚨 Early Warning<br>
        🌧️ Rain Timing<br>
        ⏱️ Rain Duration<br>
        💬 Dynamic Copilot
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("WeatherNex Prototype • SIH")

# =========================================================
# LOAD WEATHER
# =========================================================

latitude, longitude = locations[location]

try:
    weather_data = get_weather(latitude, longitude)
    current = weather_data["current"]
    hourly = prepare_hourly(weather_data)
    daily = prepare_daily(weather_data)
    timing = get_rain_timing(hourly)
    risk = calculate_risk(current, hourly)
except Exception as e:
    st.error(f"Unable to fetch weather data: {e}")
    st.stop()

temperature = safe_float(current["temperature_2m"])
humidity = safe_float(current["relative_humidity_2m"])
rainfall = safe_float(current["precipitation"])
wind_speed = safe_float(current["wind_speed_10m"])
feels_like = safe_float(current.get("apparent_temperature"))
cloud_cover = safe_float(current.get("cloud_cover"))
pressure = safe_float(current.get("surface_pressure"))

# =========================================================
# HISTORICAL + PREDICTION
# =========================================================

df = load_historical_data()
model = load_model()

if df is not None:
    location_data = df[df["location"] == location].copy()
else:
    location_data = pd.DataFrame()

if not location_data.empty:
    historical_avg = safe_float(location_data["rainfall"].mean())
else:
    historical_avg = 0

predicted_rainfall = get_prediction(
    model,
    temperature,
    humidity,
    wind_speed
)

if predicted_rainfall is None:
    predicted_rainfall = safe_float(
        daily["rainfall"].head(5).mean()
    )

if predicted_rainfall is None:
    predicted_rainfall = 0

forecast_df = pd.DataFrame({
    "Date": daily["date"].head(5),
    "Max Temperature (°C)": daily["max_temp"].head(5),
    "Min Temperature (°C)": daily["min_temp"].head(5),
    "Rainfall (mm)": daily["rainfall"].head(5),
    "Rain Probability (%)": daily["rain_probability"].head(5)
})

max_forecast_rainfall = safe_float(
    forecast_df["Rainfall (mm)"].max()
)

# =========================================================
# RISK ASSESSMENT
# =========================================================

if predicted_rainfall < 25:
    rainfall_risk = "LOW"
    warning_message = "Weather conditions are normal."

elif predicted_rainfall < 50:
    rainfall_risk = "MODERATE"
    warning_message = "Moderate rainfall expected. Stay alert."

elif predicted_rainfall < 80:
    rainfall_risk = "HIGH"
    warning_message = "Heavy rainfall expected. Prepare for possible waterlogging."

else:
    rainfall_risk = "VERY HIGH"
    warning_message = "Very heavy rainfall expected. Flood risk may increase."

alert_level, alert_message = get_alert_data(
    forecast_df,
    historical_avg
)

# =========================================================
# INTELLIGENCE SCORE
# =========================================================

rainfall_factor = min(
    predicted_rainfall / max(historical_avg, 1),
    3
)

forecast_factor = min(
    max_forecast_rainfall / max(historical_avg, 1),
    3
)

score = (
    (rainfall_factor / 3) * 50
    + (forecast_factor / 3) * 50
)

score = min(round(score), 100)

if score < 30:
    score_status = "LOW RISK"
elif score < 60:
    score_status = "MODERATE RISK"
elif score < 80:
    score_status = "HIGH RISK"
else:
    score_status = "CRITICAL RISK"

# =========================================================
# HERO
# =========================================================

now = datetime.now().strftime("%A, %d %B %Y")

st.markdown(f"""
<div class="hero">
    <h1>🌦️ WeatherNex</h1>
    <p>National Weather Intelligence Platform</p>
    <p style="margin-top:18px;color:#e0f2fe;">
        Transforming weather data into predictions,
        risk intelligence and actionable early warnings.
    </p>
    <p style="margin-top:18px;color:#bae6fd;">
        📍 {location} &nbsp; • &nbsp; {now}
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# CURRENT WEATHER
# =========================================================

st.markdown(
    '<div class="section-title">🌐 Live Weather Intelligence</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🌡️ Temperature</div>
        <div class="metric-value">{temperature:.1f}°C</div>
        <div class="metric-sub">Feels like {feels_like:.1f}°C</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💧 Humidity</div>
        <div class="metric-value">{humidity:.0f}%</div>
        <div class="metric-sub">Relative humidity</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🌧️ Current precipitation</div>
        <div class="metric-value">{rainfall:.1f}</div>
        <div class="metric-sub">mm</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💨 Wind speed</div>
        <div class="metric-value">{wind_speed:.1f}</div>
        <div class="metric-sub">km/h</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⚠️ Risk level</div>
        <div class="metric-value">{risk["level"]}</div>
        <div class="metric-sub">Score {risk["score"]}/100</div>
    </div>
    """, unsafe_allow_html=True)

# IMPORTANT: separate block with proper spacing
st.markdown(
    '<div class="section-title">🌤️ Current conditions</div>',
    unsafe_allow_html=True
)

st.markdown(f"""
<div class="info-card">
    <h3>🌤️ {weather_description(current["weather_code"])}</h3>
    <p>
        Cloud cover: <b>{cloud_cover:.0f}%</b>
        &nbsp; • &nbsp;
        Pressure: <b>{pressure:.0f} hPa</b>
        &nbsp; • &nbsp;
        Feels like: <b>{feels_like:.1f}°C</b>
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# ALERT + RAIN TIMING
# =========================================================

show_alert(risk)
rain_timing_card(timing)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Overview",
    "⏱️ Hourly Forecast",
    "📅 7-Day Forecast",
    "🗺️ Risk Map",
    "📈 Historical Analysis",
    "🚨 Early Warning",
    "🤖 Weather Copilot"
])

# =========================================================
# OVERVIEW
# =========================================================

with tab1:
    st.markdown(
        '<div class="section-title">📊 Weather Overview</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.plotly_chart(
            hourly_chart(hourly),
            use_container_width=True,
            key="overview_hourly_chart"
        )

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>💡 Smart Recommendation</h3>
            <p>
        """, unsafe_allow_html=True)

        if timing and timing["intensity"] == "Heavy":
            st.write("Heavy rain expected. Avoid unnecessary outdoor travel.")

        elif risk["level"] == "HIGH":
            st.write("Weather conditions may become disruptive. Keep backup plans.")

        elif risk["rain_probability"] >= 50:
            st.write("Carry an umbrella and check the hourly forecast before going out.")

        elif temperature >= 35:
            st.write("Temperature is high. Stay hydrated and avoid prolonged sun exposure.")

        else:
            st.write("Weather looks relatively comfortable for normal outdoor activities.")

        st.markdown("</p></div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            <h3>🧠 Intelligence Score</h3>
            <p>
                The score combines predicted rainfall and forecast rainfall
                with historical rainfall patterns.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.progress(score / 100)

        st.markdown(f"""
        <p style="color:#93c5fd;text-align:center;">
            Score: <b>{score}/100</b>
            &nbsp; • &nbsp;
            {score_status}
        </p>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">🌧️ Rainfall Analysis</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        rainfall_chart(hourly),
        use_container_width=True,
        key="overview_rainfall_chart"
    )

    st.markdown(
        '<div class="section-title">📋 Weather Situation Overview</div>',
        unsafe_allow_html=True
    )

    overview_col1, overview_col2, overview_col3 = st.columns(3)

    with overview_col1:
        st.markdown("### 🌧️ Rainfall")

        if predicted_rainfall > historical_avg:
            st.warning(
                f"Above normal\n\n"
                f"Predicted: {predicted_rainfall:.1f} mm\n\n"
                f"Average: {historical_avg:.1f} mm"
            )
        else:
            st.success(
                f"Within normal range\n\n"
                f"Predicted: {predicted_rainfall:.1f} mm\n\n"
                f"Average: {historical_avg:.1f} mm"
            )

    with overview_col2:
        st.markdown("### ⚠️ Risk")

        if score >= 80:
            st.error("CRITICAL RISK")
        elif score >= 60:
            st.warning("HIGH RISK")
        elif score >= 30:
            st.info("MODERATE RISK")
        else:
            st.success("LOW RISK")

    with overview_col3:
        st.markdown("### 🚨 Alert")

        if alert_level == "CRITICAL":
            st.error("Immediate attention required")
        elif alert_level == "HIGH":
            st.warning("Stay alert")
        elif alert_level == "MODERATE":
            st.info("Monitor conditions")
        else:
            st.success("No immediate threat")

# =========================================================
# HOURLY FORECAST
# =========================================================

with tab2:
    st.markdown(
        '<div class="section-title">⏱️ Next 24 Hours</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        hourly_chart(hourly),
        use_container_width=True,
        key="hourly_forecast_chart"
    )

    st.markdown(
        '<div class="section-title">🌧️ Rainfall Probability</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        rainfall_chart(hourly),
        use_container_width=True,
        key="hourly_rainfall_chart"
    )

    st.markdown(
        '<div class="section-title">Hourly Details</div>',
        unsafe_allow_html=True
    )

    display_hourly = hourly.head(24).copy()

    display_hourly["Time"] = display_hourly["time"].dt.strftime("%I:%M %p")
    display_hourly["Temperature"] = (
        display_hourly["temperature"].round(1).astype(str) + " °C"
    )
    display_hourly["Rain probability"] = (
        display_hourly["rain_probability"].round(0).astype(str) + "%"
    )
    display_hourly["Rainfall"] = (
        display_hourly["precipitation"].round(2).astype(str) + " mm"
    )
    display_hourly["Wind"] = (
        display_hourly["wind"].round(1).astype(str) + " km/h"
    )
    display_hourly["Condition"] = display_hourly["weather_code"].apply(
        weather_description
    )

    st.dataframe(
        display_hourly[
            ["Time", "Temperature", "Rain probability",
             "Rainfall", "Wind", "Condition"]
        ],
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# 7-DAY FORECAST
# =========================================================

with tab3:
    st.markdown(
        '<div class="section-title">📅 7-Day Weather Forecast</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        daily_chart(daily),
        use_container_width=True,
        key="daily_temperature_chart"
    )

    st.dataframe(
        forecast_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        '<div class="section-title">🌧️ 7-Day Rainfall Forecast</div>',
        unsafe_allow_html=True
    )

    fig_forecast = px.bar(
        forecast_df,
        x="Date",
        y="Rainfall (mm)",
        color="Rain Probability (%)",
        color_continuous_scale="Blues",
        title="Rainfall forecast"
    )

    fig_forecast.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    st.plotly_chart(
        fig_forecast,
        use_container_width=True,
        key="daily_rainfall_chart"
    )

# =========================================================
# RISK MAP
# =========================================================

with tab4:
    st.markdown(
        '<div class="section-title">🗺️ Regional Weather Risk Intelligence</div>',
        unsafe_allow_html=True
    )

    if not location_data.empty:
        map_data = []

        for city_name, (lat, lon) in locations.items():
            city_data = df[df["location"] == city_name]

            if not city_data.empty:
                historical_rainfall = safe_float(
                    city_data["rainfall"].mean()
                )

                if historical_rainfall < 25:
                    city_risk = "LOW"
                elif historical_rainfall < 50:
                    city_risk = "MODERATE"
                elif historical_rainfall < 80:
                    city_risk = "HIGH"
                else:
                    city_risk = "VERY HIGH"

                map_data.append({
                    "City": city_name,
                    "Latitude": lat,
                    "Longitude": lon,
                    "Historical Rainfall": historical_rainfall,
                    "Risk Level": city_risk
                })

        map_df = pd.DataFrame(map_data)

    else:
        # Fallback map so the map feature always remains visible.
        map_df = pd.DataFrame([
            {
                "City": city_name,
                "Latitude": lat,
                "Longitude": lon,
                "Historical Rainfall": 0,
                "Risk Level": "LOW"
            }
            for city_name, (lat, lon) in locations.items()
        ])

    st_folium(
        create_risk_map(map_df),
        use_container_width=True,
        height=550
    )

    st.caption(
        "Map risk is based on historical rainfall when the dataset is available."
    )

# =========================================================
# HISTORICAL ANALYSIS + AI PREDICTION
# =========================================================

with tab5:
    st.markdown(
        '<div class="section-title">📈 Historical Rainfall</div>',
        unsafe_allow_html=True
    )

    if not location_data.empty:
        fig_hist = px.line(
            location_data,
            x="date",
            y="rainfall",
            title=f"Historical rainfall — {location}"
        )

        fig_hist.update_layout(
            template="plotly_dark",
            height=400,
            margin=dict(l=10, r=10, t=50, b=10),
            xaxis_title="Date",
            yaxis_title="Rainfall (mm)"
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True,
            key="historical_rainfall_chart"
        )

    else:
        st.info(
            "Historical dataset nahi mila. "
            "Apni CSV file ko `data/weather.csv` ke naam se rakho."
        )

    st.markdown(
        '<div class="section-title">🤖 AI Rainfall Prediction</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Machine-learning based rainfall estimate using current weather conditions."
    )

    pred_col1, pred_col2, pred_col3 = st.columns(3)

    with pred_col1:
        st.metric(
            "🌧️ Predicted Rainfall",
            f"{predicted_rainfall:.1f} mm"
        )

    with pred_col2:
        st.metric(
            "📊 Historical Average",
            f"{historical_avg:.1f} mm"
        )

    with pred_col3:
        deviation = (
            (predicted_rainfall - historical_avg)
            / max(historical_avg, 1)
        ) * 100

        st.metric(
            "📈 Deviation from Average",
            f"{deviation:.1f}%"
        )

    st.markdown(
        '<div class="section-title">⚠️ Weather Risk Assessment</div>',
        unsafe_allow_html=True
    )

    risk_col1, risk_col2 = st.columns(2)

    with risk_col1:
        st.metric(
            "🌧️ Rainfall Risk",
            rainfall_risk
        )

    with risk_col2:
        if rainfall_risk == "LOW":
            st.success("✅ " + warning_message)
        elif rainfall_risk == "MODERATE":
            st.warning("⚠️ " + warning_message)
        else:
            st.error("🚨 " + warning_message)

    st.markdown(
        '<div class="section-title">🔎 Weather Anomaly Detection</div>',
        unsafe_allow_html=True
    )

    if predicted_rainfall > historical_avg * 2:
        anomaly_status = "🚨 Significant Anomaly"
        anomaly_message = (
            "Predicted rainfall is more than twice the historical average."
        )

    elif predicted_rainfall > historical_avg * 1.5:
        anomaly_status = "⚠️ Moderate Anomaly"
        anomaly_message = (
            "Predicted rainfall is significantly above the historical average."
        )

    else:
        anomaly_status = "✅ Normal"
        anomaly_message = (
            "Predicted rainfall is within the expected historical range."
        )

    anomaly_col1, anomaly_col2 = st.columns(2)

    with anomaly_col1:
        st.metric(
            "Anomaly Status",
            anomaly_status
        )

    with anomaly_col2:
        st.info(anomaly_message)

# =========================================================
# EARLY WARNING + RECOMMENDED ACTIONS + SCORE
# =========================================================

with tab6:
    st.markdown(
        '<div class="section-title">🚨 Smart Early Warning System</div>',
        unsafe_allow_html=True
    )

    warning_col1, warning_col2 = st.columns(2)

    with warning_col1:
        st.metric(
            "🌧️ Maximum Forecast Rainfall",
            f"{max_forecast_rainfall:.1f} mm"
        )

    with warning_col2:
        st.metric(
            "⚠️ Alert Level",
            alert_level
        )

    if alert_level == "CRITICAL":
        st.error("🚨 CRITICAL ALERT\n\n" + alert_message)

    elif alert_level == "HIGH":
        st.warning("⚠️ HIGH ALERT\n\n" + alert_message)

    elif alert_level == "MODERATE":
        st.info("ℹ️ MODERATE ALERT\n\n" + alert_message)

    else:
        st.success("✅ LOW RISK\n\n" + alert_message)

    st.markdown(
        '<div class="section-title">🎯 Recommended Actions</div>',
        unsafe_allow_html=True
    )

    if alert_level == "CRITICAL":
        st.error("🚨 Immediate Attention Required")

        st.markdown("""
        **Recommended Actions:**
        - Monitor weather alerts continuously
        - Avoid low-lying and waterlogged areas
        - Prepare emergency resources
        - Local authorities should remain on alert
        - Consider precautionary evacuation in vulnerable areas
        """)

    elif alert_level == "HIGH":
        st.warning("⚠️ Precautionary Action Recommended")

        st.markdown("""
        **Recommended Actions:**
        - Stay updated with weather warnings
        - Avoid unnecessary travel during heavy rainfall
        - Monitor waterlogging-prone areas
        - Authorities should prepare response teams
        """)

    elif alert_level == "MODERATE":
        st.info("ℹ️ Stay Alert")

        st.markdown("""
        **Recommended Actions:**
        - Monitor upcoming weather conditions
        - Keep local alerts enabled
        - Take normal precautions during rainfall
        """)

    else:
        st.success("✅ No Immediate Action Required")

        st.markdown("""
        **Recommended Actions:**
        - Continue monitoring weather conditions
        - No significant weather anomaly detected
        """)

    st.markdown(
        '<div class="section-title">🧠 Weather Intelligence Score</div>',
        unsafe_allow_html=True
    )

    score_col1, score_col2 = st.columns(2)

    with score_col1:
        st.metric(
            "🧠 Intelligence Score",
            f"{score}/100"
        )

    with score_col2:
        st.metric(
            "⚠️ Overall Status",
            score_status
        )

    st.progress(score / 100)

# =========================================================
# DYNAMIC COPILOT
# =========================================================

with tab7:
    st.markdown(
        '<div class="section-title">🤖 Weather Copilot</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <h3>Ask anything about the weather</h3>
        <p>
            Copilot live weather data ke according answer dega.
            Example: "Rain kab start hogi?", "Kal umbrella le jaun?",
            "Aaj outdoor plan safe hai?"
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask about weather...")

    if question:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })

        answer = copilot_response(
            question,
            location,
            current,
            hourly,
            daily,
            timing,
            risk
        )

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

    if st.button("🗑️ Clear Copilot chat"):
        st.session_state.chat_messages = []
        st.rerun()

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
<p style="text-align:center;color:#64748b;font-size:.8rem;">
    WeatherNex • Weather Intelligence Prototype • SIH
</p>
""", unsafe_allow_html=True)