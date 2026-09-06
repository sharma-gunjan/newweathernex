import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import joblib

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="WeatherNex",
    page_icon="🌦️",
    layout="wide"
)

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.header("🌦️ WeatherNex")

    st.write("National Weather Intelligence Platform")

    st.divider()

    st.subheader("📍 Location")
    st.write("Select a city from the main dashboard.")

    st.divider()

    st.subheader("🧠 Intelligence Modules")

    st.write("✅ Live Weather")
    st.write("✅ Historical Analysis")
    st.write("✅ AI Rainfall Prediction")
    st.write("✅ Risk Assessment")
    st.write("✅ Risk Map")
    st.write("✅ 5-Day Forecast")
    st.write("✅ Anomaly Detection")
    st.write("✅ Early Warning")

    st.divider()

    st.caption("WeatherNex Prototype • SIH")


# ---------------- HEADER ----------------

st.title("🌦️ WeatherNex")

st.subheader(
    "National Weather Intelligence Platform"
)

st.write(
    "Transforming weather data into predictions, "
    "risk intelligence and actionable early warnings."
)

st.divider()


# ---------------- LOCATIONS ----------------

locations = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Bengaluru": (12.9716, 77.5946)
}

location = st.selectbox(
    "📍 Select Location for Weather Intelligence",
    list(locations.keys())
)

latitude, longitude = locations[location]

st.write("Selected Location:", location)


# ---------------- WEATHER API ----------------

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),

        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "rain_sum"
        ),

        "forecast_days": 5,
        "timezone": "auto"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

    return None


weather_data = get_weather(latitude, longitude)


# ---------------- CURRENT WEATHER ----------------

if weather_data:

    st.subheader("🌐 Live Weather Intelligence")

    current = weather_data["current"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    rainfall = current["precipitation"]
    wind_speed = current["wind_speed_10m"]

    # 5-day forecast data

    daily = weather_data["daily"]

    forecast_df = pd.DataFrame({

        "Date": pd.to_datetime(daily["time"]),

        "Max Temperature (°C)":
            daily["temperature_2m_max"],

        "Min Temperature (°C)":
            daily["temperature_2m_min"],

        "Rainfall (mm)":
            daily["precipitation_sum"],

        "Rain (mm)":
            daily["rain_sum"]

    })

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🌡️ Temperature",
            f"{temperature} °C"
        )

    with col2:

        st.metric(
            "💧 Humidity",
            f"{humidity} %"
        )

    with col3:

        st.metric(
            "🌧️ Current Precipitation",
            f"{rainfall} mm"
        )

    with col4:

        st.metric(
            "💨 Wind Speed",
            f"{wind_speed} km/h"
        )

else:

    st.error("Unable to fetch weather data.")


# ---------------- HISTORICAL DATA ----------------

df = pd.read_csv("data/weather.csv")

df["date"] = pd.to_datetime(df["date"])

location_data = df[
    df["location"] == location
]


# ---------------- ML RAINFALL PREDICTION ----------------

st.subheader("🤖 AI Rainfall Prediction")

st.caption(
    "Machine-learning based rainfall estimate "
    "using current weather conditions."
)


# ---------------- LOAD ML MODEL ----------------

model = joblib.load("rainfall_model.pkl")


current_input = pd.DataFrame({

    "temperature": [temperature],

    "humidity": [humidity],

    "wind_speed": [wind_speed]

})


predicted_rainfall = model.predict(
    current_input
)[0]


# ---------------- HISTORICAL RAINFALL ----------------

st.divider()

st.subheader("📊 Historical Rainfall")

st.line_chart(
    location_data.set_index("date")["rainfall"]
)


# ---------------- HISTORICAL AVERAGE ----------------

historical_avg = location_data["rainfall"].mean()

st.metric(
    "📊 Historical Average Rainfall",
    f"{historical_avg:.1f} mm"
)


# ---------------- PREDICTION COMPARISON ----------------

st.divider()

st.subheader("🤖 AI Rainfall Prediction")

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
        / historical_avg
    ) * 100

    st.metric(
        "📈 Deviation from Average",
        f"{deviation:.1f}%"
    )


# ---------------- RISK ASSESSMENT ----------------

if predicted_rainfall < 25:

    risk_level = "LOW"

    warning_message = (
        "Weather conditions are normal."
    )

elif predicted_rainfall < 50:

    risk_level = "MODERATE"

    warning_message = (
        "Moderate rainfall expected. Stay alert."
    )

elif predicted_rainfall < 80:

    risk_level = "HIGH"

    warning_message = (
        "Heavy rainfall expected. "
        "Prepare for possible waterlogging."
    )

else:

    risk_level = "VERY HIGH"

    warning_message = (
        "Very heavy rainfall expected. "
        "Flood risk may increase."
    )


# ---------------- WEATHER RISK ASSESSMENT ----------------

st.divider()

st.subheader("⚠️ Weather Risk Assessment")

st.caption(
    "Risk level is estimated using predicted rainfall "
    "and historical rainfall patterns."
)

risk_col1, risk_col2 = st.columns(2)

with risk_col1:

    st.metric(
        "🌧️ Rainfall Risk",
        risk_level
    )

with risk_col2:

    if risk_level == "LOW":

        st.success(
            "✅ " + warning_message
        )

    elif risk_level == "MODERATE":

        st.warning(
            "⚠️ " + warning_message
        )

    else:

        st.error(
            "🚨 " + warning_message
        )


# ---------------- SMART RISK MAP ----------------

st.divider()

st.subheader("🗺️ Regional Weather Risk Intelligence")

map_data = []

for city, (lat, lon) in locations.items():

    city_data = df[
        df["location"] == city
    ]

    if not city_data.empty:

        historical_rainfall = (
            city_data["rainfall"].mean()
        )

        # Estimate city risk
        # from historical rainfall

        if historical_rainfall < 25:

            city_risk = "LOW"

        elif historical_rainfall < 50:

            city_risk = "MODERATE"

        elif historical_rainfall < 80:

            city_risk = "HIGH"

        else:

            city_risk = "VERY HIGH"

        map_data.append({

            "City": city,

            "Latitude": lat,

            "Longitude": lon,

            "Historical Rainfall":
                round(historical_rainfall, 1),

            "Risk Level": city_risk

        })


map_df = pd.DataFrame(map_data)


fig = px.scatter_map(

    map_df,

    lat="Latitude",

    lon="Longitude",

    hover_name="City",

    hover_data={

        "Historical Rainfall": True,

        "Risk Level": True,

        "Latitude": False,

        "Longitude": False

    },

    color="Risk Level",

    zoom=4,

    height=550,

    title="Weather Risk Across Selected Regions"

)

fig.update_layout(

    map_style="open-street-map",

    margin={
        "r": 0,
        "t": 50,
        "l": 0,
        "b": 0
    }

)

st.plotly_chart(

    fig,

    use_container_width=True,

    key="regional_weather_risk_map"

)


# ---------------- 5-DAY FORECAST ----------------

st.divider()

st.subheader("📅 5-Day Weather Forecast")

st.dataframe(

    forecast_df,

    use_container_width=True,

    hide_index=True

)


st.subheader("🌧️ 5-Day Rainfall Forecast")

forecast_chart = forecast_df.set_index(
    "Date"
)[["Rainfall (mm)"]]

st.line_chart(forecast_chart)


# ---------------- SMART EARLY WARNING ----------------

max_forecast_rainfall = forecast_df[
    "Rainfall (mm)"
].max()

max_rainfall_date = forecast_df.loc[

    forecast_df["Rainfall (mm)"].idxmax(),

    "Date"

]


# Compare forecast with historical average

if max_forecast_rainfall > historical_avg * 2:

    alert_level = "CRITICAL"

    alert_message = (

        f"Very heavy rainfall is expected around "

        f"{max_rainfall_date.strftime('%d %b')}. "

        f"Potential waterlogging risk."

    )

elif max_forecast_rainfall > historical_avg * 1.5:

    alert_level = "HIGH"

    alert_message = (

        f"Heavy rainfall is expected around "

        f"{max_rainfall_date.strftime('%d %b')}. "

        f"Residents should remain alert."

    )

elif max_forecast_rainfall > historical_avg:

    alert_level = "MODERATE"

    alert_message = (

        f"Rainfall may be above the historical average "

        f"around {max_rainfall_date.strftime('%d %b')}."

    )

else:

    alert_level = "LOW"

    alert_message = (

        "No significant rainfall anomaly detected "

        "in the forecast period."

    )


# ---------------- SMART EARLY WARNING SYSTEM ----------------

st.divider()

st.subheader("🚨 Smart Early Warning System")

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

    st.error(

        "🚨 CRITICAL ALERT\n\n"
        + alert_message

    )

elif alert_level == "HIGH":

    st.warning(

        "⚠️ HIGH ALERT\n\n"
        + alert_message

    )

elif alert_level == "MODERATE":

    st.info(

        "ℹ️ MODERATE ALERT\n\n"
        + alert_message

    )

else:

    st.success(

        "✅ LOW RISK\n\n"
        + alert_message

    )


# ---------------- WEATHER ANOMALY DETECTION ----------------

st.divider()

st.subheader("🔎 Weather Anomaly Detection")

if predicted_rainfall > historical_avg * 2:

    anomaly_status = "🚨 Significant Anomaly"

    anomaly_message = (

        "Predicted rainfall is more than twice "
        "the historical average."

    )

elif predicted_rainfall > historical_avg * 1.5:

    anomaly_status = "⚠️ Moderate Anomaly"

    anomaly_message = (

        "Predicted rainfall is significantly above "
        "the historical average."

    )

else:

    anomaly_status = "✅ Normal"

    anomaly_message = (

        "Predicted rainfall is within the expected "
        "historical range."

    )


anomaly_col1, anomaly_col2 = st.columns(2)

with anomaly_col1:

    st.metric(

        "Anomaly Status",

        anomaly_status

    )

with anomaly_col2:

    st.info(anomaly_message)


# ---------------- ACTION RECOMMENDATION ----------------

st.divider()

st.subheader("🎯 Recommended Actions")

if alert_level == "CRITICAL":

    st.error("🚨 Immediate Attention Required")

    st.write("""
    **Recommended Actions:**

    - Monitor weather alerts continuously
    - Avoid low-lying and waterlogged areas
    - Prepare emergency resources
    - Local authorities should remain on alert
    - Consider precautionary evacuation in vulnerable areas
    """)

elif alert_level == "HIGH":

    st.warning("⚠️ Precautionary Action Recommended")

    st.write("""
    **Recommended Actions:**

    - Stay updated with weather warnings
    - Avoid unnecessary travel during heavy rainfall
    - Monitor waterlogging-prone areas
    - Authorities should prepare response teams
    """)

elif alert_level == "MODERATE":

    st.info("ℹ️ Stay Alert")

    st.write("""
    **Recommended Actions:**

    - Monitor upcoming weather conditions
    - Keep local alerts enabled
    - Take normal precautions during rainfall
    """)

else:

    st.success("✅ No Immediate Action Required")

    st.write("""
    **Recommended Actions:**

    - Continue monitoring weather conditions
    - No significant weather anomaly detected
    """)


# ---------------- WEATHER INTELLIGENCE SCORE ----------------

st.divider()

st.subheader("🧠 Weather Intelligence Score")

rainfall_factor = min(

    predicted_rainfall
    / max(historical_avg, 1),

    3

)

forecast_factor = min(

    max_forecast_rainfall
    / max(historical_avg, 1),

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


# ---------------- WEATHER SITUATION OVERVIEW ----------------

st.divider()

st.subheader("📋 Weather Situation Overview")

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
