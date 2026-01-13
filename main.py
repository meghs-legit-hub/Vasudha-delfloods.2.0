import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Page setup
st.set_page_config(page_title="Flood Prediction System", layout="centered")
st.title("🌊 Flood Prediction & Early Warning System")
st.write("ML + Copernicus Marine Data (Global Ocean Model)")

# City configuration
CITY_CONFIG = {
    "Delhi": {
        "type": "inland",
        "location": "Delhi,IN",
        "river_warning": 202.0,
        "river_danger": 205.55,
        "lat": 28.6139,
        "lon": 77.2090
    },
    "Mumbai": {
        "type": "coastal",
        "location": "Mumbai,IN",
        "river_warning": 3.5,
        "river_danger": 4.5,
        "lat": 18.9640,
        "lon": 72.8205
    },
    "Chennai": {
        "type": "coastal",
        "location": "Chennai,IN",
        "river_warning": 2.0,
        "river_danger": 3.0,
        "lat": 13.0827,
        "lon": 80.2707
    }
}

city = st.selectbox("📍 Select City / District", list(CITY_CONFIG.keys()))
city_info = CITY_CONFIG[city]

#Training the model
def train_model():
    df = pd.read_csv("new_csv.csv")
    X = df[['precip', 'River_Level', 'temp', 'humidity', 'windspeed']]
    y = df['Flood']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100) #random_state=42 after 100?
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return model, accuracy

# Train model/test accuracy
model, accuracy = train_model()

# Input for river level
river_level = st.number_input("🌊 Enter current river level (in meters):", min_value=0.0, step=0.1) 
#river_level = st.number_input(f"🌊 Enter river level for {city} (meters)",min_value=0.0,step=0.1)


# ✅ Function to safely fetch weather data
def fetch_weather_data(location):
   # location = "Delhi,IN"
    today = datetime.now().strftime("%Y-%m-%d")
    api_key = "HC8QD5Y25CNY89PCZB3643W4X"

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{today}/{today}"
    params = {
        "unitGroup": "metric",
        "include": "days",
        "key": api_key,
        "contentType": "json"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "days" in data and len(data["days"]) > 0:
            today_data = data["days"][0]
            return {
                "precip": today_data.get("precip") or 0.0,
                "temp": today_data.get("temp") or 0.0,
                "humidity": today_data.get("humidity") or 0.0,
                "windspeed": today_data.get("windspeed") or 0.0
            }
    return None

#Copernicus Marine: Sea Surface Height Anomaly
def fetch_sea_surface_height(lat, lon):
    url = "https://my.cmems-du.eu/thredds/ncss/grid/global-analysis-forecast-phy-001-024/ssh"
    params = {
        "var": "zos",
        "latitude": lat,
        "longitude": lon,
        "time": "latest",
        "accept": "json"
    }

    response = requests.get(
        url,
        params=params,
        auth=(st.secrets["COPERNICUS_USER"], st.secrets["COPERNICUS_PASS"])
    )

    if response.status_code == 200:
        data = response.json()
        try:
            return float(data["data"][0]["zos"])
        except:
            return 0.0
    return 0.0
# Get weather
weather = fetch_weather_data(city_info["location"])
sea_level_anomaly = 0.0

if city_info["type"] == "coastal":
    sea_level_anomaly = fetch_sea_surface_height(city_info["lat"], city_info["lon"])
    

# Make prediction if both inputs are ready
if weather and river_level:
    st.subheader("📊 Today's Weather Data:") #st.subheader("📊 Live Environmental Data")
    st.json(weather)

    if city_info["type"] == "coastal":
        st.write(f"🌊 Sea Surface Height Anomaly (Copernicus): "f"**{round(sea_level_anomaly, 2)} m**")

    # Format data for prediction
    input_data = pd.DataFrame([{
        'precip': weather['precip'],
        'River_Level': river_level,
        'temp': weather['temp'],
        'humidity': weather['humidity'],
        'windspeed': weather['windspeed']
    }])

      # Show river level rule-based prediction
    st.subheader("📢 Flood Risk Assessment")
    if city_info["type"] == "inland":
        if river_level > 205.55:
            st.error("🔴 ALERT: River flooding WILL LIKELY occur.")
        elif river_level > 202:
            st.warning("🟠 WARNING: River flooding is POSSIBLE.")
        else:
            st.success("🟢 River flooding is NOT EXPECTED.")
    else:
        if sea_level_anomaly > 0.4 and weather["precip"] > 50:
            st.error("🔴 Coastal flooding VERY LIKELY (surge + rainfall).")
        elif sea_level_anomaly > 0.2:
            st.warning("🟠 Elevated sea level detected.")
        else:
            st.success("🟢 Coastal conditions stable.")


     # Also run the model prediction
    prediction = model.predict(input_data)[0]
    st.subheader("📊 Model-Based Prediction:")
    if prediction == 2:
        st.error("🚩 Model says: FLOOD HIGHLY LIKELY – Stay safe!")
    elif prediction == 1:
        st.warning("⚠️ Model says: FLOOD LIKELY – Stay safe!")
    else:
        st.success("✅ Model says: NO FLOOD expected today.")

st.write("✅ Model accuracy:", round(accuracy * 100, 2), "%")



#st.write("✅ Model accuracy on test data:", accuracy)












